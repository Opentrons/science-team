import math
from opentrons.types import Point

# metadata
metadata = {
    'protocolName': 'Seqwell - SB start and stop reaction',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.3'
}

NUM_PLATES = 1
NUM_SAMPLES = 96


def run(ctx):

    # load labware

    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magdeck', '6')

    tc_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '3')
    tc_plate2 = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')
    #strips = tempdeck.load_labware('usascientific_200ul_pcrstrip')
    #strips = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    strips = tempdeck.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul')
    dna_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '1')
    dna_plate2 = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2')
    tipracks20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
                  for slot in ['5', '7', '8', '9', '10', '11']]

    # pipettes
    m20 = ctx.load_instrument(
        'p20_multi_gen2', mount='left', tip_racks=tipracks20)

    tip_count = 0
    tip_max = len(tipracks20)*12

    def pick_up():
        nonlocal tip_count
        if tip_count == tip_max:
            ctx.pause('Replace empty tipracks before resuming')
            m20.reset_tipracks()
            tip_count = 0
        tip_count += 1
        m20.pick_up_tip()

    # samples and reagents
    num_cols = math.ceil(NUM_SAMPLES/8)
    dna_samples_m = dna_plate.rows()[0][:num_cols]
    dna_samples_m2 = dna_plate2.rows()[0][:num_cols]
    tc_samples_m = tc_plate.rows()[0][:num_cols]
    tc_samples_m2 = tc_plate2.rows()[0][:num_cols]

    coding_buffer_strip = strips.columns()[0]
    x_solution_strip = strips.columns()[1]

    m20.flow_rate.aspirate = 0.765
    m20.flow_rate.dispense = 0.765
    withdrawal_speed 	   = 1 #mm/s
    #m20.flow_rate.blow_out = 100

    # translate starting vol to starting height
    starting_vol = num_cols*NUM_PLATES*4
    h = round((starting_vol/200)*coding_buffer_strip[0].geometry._depth, 2)
    dh = round(h/(num_cols*NUM_PLATES)*1.5, 2)

    for d in tc_samples_m:
        # calculate height
        if h - dh >= 0.1:
            h -= dh
        else:
            h = 0.1

        pick_up()
        m20.aspirate(4, coding_buffer_strip[0].bottom(h))
        m20.move_to(coding_buffer_strip[0].top(4),speed=withdrawal_speed)
        #m20.touch_tip(v_offset=-3)
        #m20.air_gap(2)
        m20.dispense(6, d.bottom())
        m20.flow_rate.aspirate = 2
        m20.flow_rate.dispense = 2
        m20.mix(6, 3)
        m20.flow_rate.aspirate = 0.765
        m20.flow_rate.dispense = 0.765
        m20.move_to(d.top(),speed=withdrawal_speed)
        #m20.touch_tip(v_offset=-3)
        m20.flow_rate.blow_out = 100
        m20.blow_out()

        #m20.flow_rate.aspirate = 7.6
        #m20.flow_rate.dispense = 7.6
        #m20.air_gap(5)
        m20.drop_tip()