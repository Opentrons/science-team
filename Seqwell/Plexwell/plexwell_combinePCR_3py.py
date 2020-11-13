#Combine PCR pools Protocol 3/9
#last update: october 15, 2020
#Seqwell Workflow

import math

metadata = {
    'apiLevel': '2.3'
}

NUM_PLATES = 2
NUM_SAMPLES = 96


def run(ctx):
    
    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')

    pool2_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2')


    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
              for slot in ['7', '8']]
    pool1_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '1')
    pool1_plate2 = tempdeck.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul')
    pool2_plate2 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    pool_combined_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '3')
    pool_combined_plate2 = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks=tips20)

    # reagents
    num_cols = math.ceil(NUM_SAMPLES/8)

    tip_max = len(tips20)*12
    tip_count = 0

    def pick_up():
        nonlocal tip_count
        if tip_max == tip_count:
            m20.home()
            ctx.pause('Replace 20µl tipracks before resuming.')
            m20.reset_tipracks()
            tip_count = 0
        tip_count += 1
        m20.pick_up_tip()

    # pool samples
    for n in range(num_cols):
        pick_up()
        m20.consolidate(
            3, [plate.rows()[0][n] for plate in [pool1_plate, pool2_plate]],
            pool_combined_plate.rows()[0][n], mix_after=(3,3), new_tip='never')
        m20.drop_tip()

    if NUM_PLATES == 2:
        for n in range(num_cols):
            pick_up()
            m20.consolidate(
                3, [plate.rows()[0][n] for plate in [pool1_plate2, pool2_plate2]],
                pool_combined_plate2.rows()[0][n], mix_after=(3,3), new_tip='never')
            m20.drop_tip()
