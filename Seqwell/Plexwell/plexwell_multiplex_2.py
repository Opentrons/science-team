#Multiplex PCR set up Protocol 2/9
#last update: December 20, 2020
#Seqwell Workflow

import math

metadata = {
    'apiLevel': '2.3'
}
NUM_SAMPLES = 96


def run(ctx):
    dna_sample_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '1')

    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')

    mm_strips = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    pool2_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '3')
    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
              for slot in ['5','7', '8', '9', '10', '11']]
    pool1_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '2')

    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks=tips20)

    magplate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    # reagents
    num_cols = math.ceil(NUM_SAMPLES/8)
    pool1_mm = mm_strips.rows()[0][:2]
    pool2_mm = mm_strips.rows()[0][2:4]

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


    # ghost pickup to load and sense magnetic module to avoid crash
    pick_up()
    m20.move_to(magplate.wells()[0].top(3))

    # transfer sample to pool plates
    for i in range(num_cols):
        if not m20.hw_pipette['has_tip']:
            pick_up()
        for plate in [pool1_plate, pool2_plate]:
            m20.transfer(5, dna_sample_plate.columns()[i][0],
                         plate.columns()[i][0].bottom(0.5), air_gap=2,
                         new_tip='never')
        m20.drop_tip()

    # transfer mastermix to each pool plate
    for mm, plate in zip([pool1_mm, pool2_mm], [pool1_plate, pool2_plate]):
        for i, d in enumerate(plate.rows()[0][:num_cols]):
            pick_up()
            m20.transfer(20, mm[i//6], d.top(), air_gap=2,
                         new_tip='never')
            m20.mix(5, 10, d)
            m20.air_gap(2)
            m20.drop_tip()

    ctx.comment('Place pool 1 and pool 2 plate on off deck thermocyclers \
    and run the PCR program')
