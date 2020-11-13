#PB Reaction and purification Protocol 8/9
#last update: October 30, 2020
#Seqwell Workflow

import math
from opentrons import types

metadata = {
    'protocolName': 'SeqWell - Pooled Barcoding and Purification',
    'author': 'Chaz <chaz@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.3'
}

NUM_POOL = 16  # this should be between 1 and 16


def run(protocol):
    # load labware, modules, and pipettes
    tips20 = [protocol.load_labware(
                'opentrons_96_filtertiprack_20ul', s) for s in ['5', '10']]

    tips200 = [protocol.load_labware(
                'opentrons_96_filtertiprack_200ul', s) for s in [
                    '7', '8', '9', '11']]

    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=tips20)

    m300 = protocol.load_instrument(
        'p300_multi_gen2', 'left', tip_racks=tips200)

    tempdeck = protocol.load_module('temperature module gen2', '4')
    magdeck = protocol.load_module('magnetic module gen2', '6')

    pcr_strips = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul',
#         'nest_96_wellplate_100ul_pcr_full_skirt',
        '1', 'PCR Strips')

    thermo_strips = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul',
#         'nest_96_wellplate_100ul_pcr_full_skirt',
        '2', 'Thermocycler + Destination Strips')

    al_block24 = tempdeck.load_labware(
        'opentrons_24_aluminumblock_nest_0.5ml_screwcap', 'PB Reagents')
#         'opentrons_24_aluminumblock_nest_1.5ml_snapcap', 'PB Reagents')

    deep_plate = magdeck.load_labware('nest_96_wellplate_2ml_deep')

    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '3')

    if NUM_POOL < 1 or NUM_POOL > 16:
        raise Exception('Number of Pools must be between 1 and 16.')

    num_col = math.ceil(NUM_POOL/8)

    tempdeck.set_temperature(4)
    p20.flow_rate.aspirate = 7.6
    p20.flow_rate.dispense = 7.6
    p20.flow_rate.blow_out = 100
    m300.flow_rate.aspirate = 100
    m300.flow_rate.dispense = 200
    m300.flow_rate.blow_out = 500

    """
    ~~~ 5. Pool Barcoding (PB) Reaction Setup ~~~
    """
    protocol.comment('Beginning Step 5. Pool Barcoding Reaction Setup...')

    # Add 5ul of PB Reagent to each SB tube
    pb_reagents = al_block24.wells()[:NUM_POOL]
    init_sb = pcr_strips.wells()[80:80+NUM_POOL]
    protocol.comment('Adding 5uL of PB reagent to each SB tube.')
    for pb, dest in zip(pb_reagents, init_sb):
        p20.pick_up_tip()
        p20.aspirate(5, pb)
        p20.touch_tip()
        p20.air_gap(3)
        p20.dispense(8, dest)
        p20.mix(5, 20, dest)
        p20.touch_tip()
        p20.blow_out()
        p20.drop_tip()

    # Add 22ul of Coding Buffer to PCR tube containing SB pool
    coding_buffer = pcr_strips['A1']
    init_row = pcr_strips.rows()[0][10:10+num_col]
    protocol.comment('Adding 22uL of Coding Buffer to each SB tube.')
    for sb in init_row:
        m300.pick_up_tip()
        m300.flow_rate.aspirate = 25
        m300.flow_rate.dispense = 50
        m300.aspirate(22, coding_buffer)
        m300.air_gap(10)
        m300.dispense(32, sb)
        m300.mix(2, 60, sb)
        m300.flow_rate.aspirate = 100
        m300.flow_rate.dispense = 200
        m300.blow_out()
        m300.drop_tip()

    protocol.pause('Step 5 complete. Please cap PCR tubes containing PB \
        reaction and run TAG program on thermal cycler. After TAG program, \
        return strips to deck and click RESUME to begin Step 6.')

    """
    ~~~ 6. PB Reaction Stop ~~~
    """
    protocol.comment('Beginning Step 6. PB Reaction Stop...')

    # Add 31uL of X solution to each PB Reaction
    x_solution = [pcr_strips[pos] for pos in ['A2', 'A3']]
    pb_react = [
        [thermo_strips['A1'], thermo_strips['A2']],
        [thermo_strips['A3'], thermo_strips['A4']]
        ][:num_col]
    protocol.comment('Splitting up sample.')
    for src, dest in zip(init_row, pb_react):
        m300.pick_up_tip()
        m300.aspirate(66, src)
        for d in dest:
            m300.dispense(33, d)
        m300.blow_out()
        m300.drop_tip()

    protocol.comment('Adding 31uL of X solution to each reaction tube.')
    for x, pb_dest in zip(x_solution, pb_react):
        for pb in pb_dest:
            m300.pick_up_tip()
            m300.aspirate(31, x)
            m300.air_gap(10)
            m300.dispense(41, pb)
            m300.flow_rate.aspirate = 25
            m300.flow_rate.dispense = 50
            m300.mix(5, 50, pb)
            m300.blow_out()
            m300.drop_tip()
            m300.flow_rate.aspirate = 100
            m300.flow_rate.dispense = 200

    protocol.pause('Step 6 complete. Please cap PCR tubes containging PB \
        reaction and run STOP program on thermal cycler. After TAG program,\
         return strips to deck and click RESUME to begin Step 7.')

    """
    ~~~ 7. PB Reaction Purification ~~~
    """
    protocol.comment('Beginning Step 7. PB Reaction Purification...')
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
        extra_vol = 0
        while vol > 200:
            m300.aspirate(
                180, loc.bottom().move(types.Point(x=side, y=0, z=0.5)))
            m300.dispense(180, liq_waste.top(-3))
            m300.aspirate(10, liq_waste.top())
            vol -= 180
            extra_vol += 10
        m300.aspirate(
            vol, loc.bottom().move(types.Point(x=side, y=0, z=0.5)))
        m300.dispense(vol+extra_vol, liq_waste.top(-3))
        m300.flow_rate.aspirate = 100

    protocol.comment('Adding 99uL of MAGwise to deep well plate')
    mag_samps = deep_plate.rows()[0][:num_col]
    m300.pick_up_tip()
    m300.mix(10, 200, magwise)
    for m in mag_samps:
        m300.aspirate(99, magwise)
        m300.air_gap(10)
        m300.dispense(109, m)
        m300.blow_out()
    m300.drop_tip()

    protocol.comment('Adding PB reaction to deep well plate.')
    for tube, samp, s in zip(pb_react, mag_samps, side_vars):
        m300.pick_up_tip()
        for t in tube:
            m300.aspirate(64, t)
        m300.air_gap(20)
        m300.dispense(148, samp)
        deep_mix(10, 180, samp, s)
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
        supernatant_removal(227, samp, s)
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
        protocol.comment('Incubating for 30 seconds.')
        protocol.delay(seconds=30)
        protocol.comment('Removing supernatant.')
        for samp, s in zip(mag_samps, side_vars):
            m300.pick_up_tip()
            supernatant_removal(320, samp, s)
            m300.drop_tip()

    protocol.comment('Adding 24uL of 10mM Tris to bead pellets.')
    magdeck.disengage()
    for samp, s in zip(mag_samps, side_vars):
        m300.pick_up_tip()
        m300.aspirate(24, tris)
        m300.air_gap(10)
        m300.dispense(34, samp)
        deep_mix(10, 30, samp, s)
        m300.blow_out()
        m300.drop_tip()

    protocol.comment('Incubating to allow DNA to elute.')
    protocol.delay(minutes=5)
    protocol.comment('Engaging MagDeck')
    magdeck.engage(height=13.7)
    protocol.comment('Waiting for bead pellet to form.')
    protocol.delay(minutes=2)

    final_tube = thermo_strips.rows()[0][10:10+num_col]
    protocol.comment('Transferring elution to PCR tubes.')
    m300.flow_rate.aspirate = 20
    for src, dest, side in zip(mag_samps, final_tube, side_vars):
        m300.pick_up_tip()
        m300.aspirate(23, src.bottom().move(types.Point(x=side, y=0, z=0.5)))
        m300.dispense(23, dest)
        m300.blow_out()
        m300.drop_tip()

    protocol.comment('Protocol complete! Proceed immediately to next step \
    (library amplification) or store purified PB reaction at -20C.')
