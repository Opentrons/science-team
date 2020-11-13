#Library prep Protocol 9/9
#last update: October 1, 2020
#Seqwell Workflow

import math
from opentrons import types

metadata = {
    'protocolName': 'SeqWell - Library Amplification & Purification',
    'author': 'Chaz <chaz@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.3'
}

NUM_POOL = 16  # this should be between 1 and 16
TRIS_VOL = 180  # the amount of Tris needed in Step 9-B to get to 205uL


def run(protocol):
    # load labware, modules, and pipettes
    tips20 = [protocol.load_labware(
                'opentrons_96_filtertiprack_20ul', s) for s in ['5', '10']]

    tips200 = [protocol.load_labware(
                'opentrons_96_filtertiprack_200ul', str(s)
                ) for s in [8, 9, 11]]

    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=tips20)

    m300 = protocol.load_instrument(
        'p300_multi_gen2', 'left', tip_racks=tips200)

    tempdeck = protocol.load_module('temperature module gen2', '4')
    magdeck = protocol.load_module('magnetic module gen2', '6')

    input_strips = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul',
        '1', 'PCR Strips')

    """output_strips = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul',
        '2', 'Thermocycler + Destination Strips')"""

    al_block96 = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul',
        '96-Well Aluminum Block + PCR Strips')

    elution_tubes = protocol.load_labware(
        'opentrons_24_aluminumblock_nest_1.5ml_snapcap',
        '2'
    )

    deep_plate = magdeck.load_labware('nest_96_wellplate_2ml_deep')

    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '3')

    if NUM_POOL < 1 or NUM_POOL > 16:
        raise Exception('Number of Pools must be between 1 and 16.')

    num_col = math.ceil(NUM_POOL/8)
    magdeck.engage(height=13.7)
    
#    tempdeck.set_temperature(4)
    p20.flow_rate.aspirate = 10
    p20.flow_rate.dispense = 20
    p20.flow_rate.blow_out = 100
    m300.flow_rate.aspirate = 100
    m300.flow_rate.dispense = 200
    m300.flow_rate.blow_out = 500

    """
    ~~~ 8. Library Amplification ~~~
    """
    protocol.comment('Beginning Step 8. Library Amplification...')

    input_samps = input_strips.rows()[0][:num_col]
    mastermix = al_block96['A1']

    protocol.comment('Adding 4uL Library Primer Mix + 27uL Kapa HiFi.')
    for samp in input_samps:
        m300.pick_up_tip()
        m300.aspirate(31, mastermix)
        m300.air_gap(10)
        m300.dispense(41, samp)
        m300.mix(10, 40, samp)
        m300.blow_out()
        m300.drop_tip()

    protocol.pause('Step 8 complete. Please cap PCR tubes containing sample \
        reaction and run FILL_AMP program on thermal cycler. After FILL_AMP \
        program, return strips to deck and click RESUME to begin Step 9.')

    """
    ~~~ 9. Library Purification ~~~
    """
    protocol.comment('Beginning Step 9. Library Purification...')

    amp_samps = input_strips.rows()[0][10:10+num_col]
    mag_samps = deep_plate.rows()[0][:num_col]
    mag_samps_s = deep_plate.wells()[:NUM_POOL]
    freeze_samps = al_block96.rows()[0][10:10+num_col]
    # ctrl_samps = output_strips.rows()[0][num_col:num_col+num_col]
    ctrl_samps_s = al_block96.wells()[80:80+NUM_POOL]
    magwise = reservoir['A1']
    etoh = reservoir['A2']
    tris = reservoir['A3']
    liq_waste = reservoir['A12']

    side_vars = [-1, 1]

    def deep_mix(reps, vol, loc, side):
        """Function for improved mixing of magbeads in deep well"""

        loc1 = loc.bottom().move(types.Point(x=side, y=0, z=0.6))
        alt_mix = side * -1
        loc2 = loc.bottom().move(types.Point(x=alt_mix, y=0, z=1))
        for _ in range(reps):
            m300.aspirate(vol, loc1)
            m300.dispense(vol, loc2)

    def supernatant_removal(vol, loc, side):
        """Function for removal of supernatant"""

        m300.flow_rate.aspirate = 20
        while vol > 200:
            m300.aspirate(
                180, loc.bottom().move(types.Point(x=side, y=0, z=0.5)))
            m300.dispense(180, liq_waste.top(-3))
            m300.aspirate(10, liq_waste.top())
            vol -= 180
        m300.aspirate(
            vol, loc.bottom().move(types.Point(x=side, y=0, z=0.5)))
        m300.dispense(vol, liq_waste.top(-3))
        m300.flow_rate.aspirate = 100

    protocol.comment('Adding %duL 10mM Tris to sample' % TRIS_VOL)

    for samp, mag, ctrl in zip(amp_samps, mag_samps, freeze_samps):
        m300.pick_up_tip()
        m300.aspirate(TRIS_VOL, tris)
        m300.air_gap()
        m300.dispense(200, samp)
        m300.mix(8, 200, samp)
        m300.aspirate(100, samp)
        m300.air_gap(20)
        m300.dispense(120, ctrl)
        m300.aspirate(105, samp)
        m300.air_gap(20)
        m300.dispense(125, mag)
        m300.drop_tip()

    protocol.comment('Adding 5uL of sample to PCR tubes for control.')
    for samp, ctrl in zip(mag_samps_s, ctrl_samps_s):
        p20.pick_up_tip()
        p20.aspirate(5, samp)
        p20.dispense(5, ctrl)
        p20.blow_out()
        p20.drop_tip()

    protocol.comment('Adding 75uL of MAGwise to deep well plate')

    for samp, side in zip(mag_samps, side_vars):
        m300.pick_up_tip()
        m300.mix(6, 200, magwise)
        m300.aspirate(75, magwise)
        m300.air_gap(10)
        m300.dispense(85, samp)
        deep_mix(10, 160, samp, side)
        m300.blow_out()
        m300.drop_tip()

    protocol.comment('Incubating to allow DNA to bind.')
    protocol.delay(minutes=5)
    protocol.comment('Engaging MagDeck')
    magdeck.engage(height=13.7)
    protocol.comment('Waiting for bead pellet to form.')
    protocol.delay(minutes=3)

    protocol.comment('Removing supernatant.')
    for samp, s in zip(mag_samps, side_vars):
        m300.pick_up_tip()
        supernatant_removal(175, samp, s)
        m300.drop_tip()

    for idx in range(1, 3):
        protocol.comment('Ethanol wash %d:' % idx)
        protocol.comment('Adding 300ul of ethanol.')
        for samp in mag_samps:
            m300.pick_up_tip()
            m300.flow_rate.dispense = 50
            m300.aspirate(150, etoh)
            m300.dispense(150, samp.bottom(5))
            m300.aspirate(150, etoh)
            m300.dispense(150, samp.bottom(5))
            m300.drop_tip()
            m300.flow_rate.dispense = 200
#        protocol.comment('Incubating for 30 seconds.')
#        protocol.delay(seconds=30)
        protocol.comment('Removing supernatant.')
        for samp, s in zip(mag_samps, side_vars):
            m300.pick_up_tip()
            supernatant_removal(320, samp, s)
            m300.drop_tip()

    protocol.comment('Adding 32uL of 10mM Tris to bead pellets.')
    magdeck.disengage()
    for samp, s in zip(mag_samps, side_vars):
        m300.pick_up_tip()
        m300.aspirate(32, tris)
        m300.air_gap(10)
        m300.dispense(42, samp)
        deep_mix(10, 30, samp, s)
        m300.blow_out()
        m300.drop_tip()

    protocol.comment('Incubating to allow DNA to elute.')
    protocol.delay(minutes=5)
    protocol.comment('Engaging MagDeck')
    magdeck.engage(height=13.7)
    protocol.comment('Waiting for bead pellet to form.')
    protocol.delay(minutes=2)

    final_tube = elution_tubes.wells()[:NUM_POOL]
    protocol.comment('Transferring elution to PCR tubes.')
    m300.flow_rate.aspirate = 20
    side_num = 0
    for src, dest in zip(mag_samps_s, final_tube):
        p20.pick_up_tip()
        side = side_vars[0] if side_num < 8 else side_vars[1]
        p20.transfer(
            28, src.bottom().move(types.Point(x=side, y=0, z=0.5)),
            dest, new_tip='never')
        p20.blow_out()
        p20.drop_tip()
        side_num += 1

    protocol.comment('Protocol complete!')
