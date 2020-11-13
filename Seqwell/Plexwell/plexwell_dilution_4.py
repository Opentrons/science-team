#Global dilution Protocol 4/9
#Last update: october 15, 2020
#Seqwell Workflow

import math


metadata = {
    'apiLevel': '2.3'
}
NUM_PLATES = 1 #minimum is 1, maximum is 2
VOL_TRIS_1 = 20 #volume of tris in 1st plate
VOL_TRIS_2 = 30 #volume of tris in 2nd plate
SAMPLE_VOL = 5 #the volume from STOCK plate 1
SAMPLE_VOL2 = 6 #the volume from STOCK plate 2


NUM_SAMPLES = 96
MIX_VOLUME = 30


def run(ctx):

    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')
    #magdeck = ctx.load_module('magdeck', '6')

    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
              for slot in ['7', '8']]
    tips200 = [ctx.load_labware('opentrons_96_filtertiprack_200ul', slot)
              for slot in ['9', '10']]
    #tris = ctx.load_labware('nest_1_reservoir_195ml', '1').wells()[0]
    tris = ctx.load_labware('agilent_96_reservoir_300000ul', '1').rows()[0][6]
    sample1 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '2')
    sample2 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '3')
    plate1 = tempdeck.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul')
    plate2 = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '5')


    magplate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks=tips20)
    m20.flow_rate.aspirate = 100
    m20.flow_rate.dispense = 100
    m300 = ctx.load_instrument('p300_multi_gen2', 'right', tip_racks=tips200)
    m300.flow_rate.aspirate = 100
    m300.flow_rate.dispense = 100

    # reagents
    num_cols = math.ceil(NUM_SAMPLES/8)
    samples = sample1.rows()[0][:num_cols]
    samples2 = sample2.rows()[0][:num_cols]
    dest = plate1.rows()[0][:num_cols]
    dest2 = plate2.rows()[0][:num_cols]

    tip_max = len(tips20)*12
    tip_count = 0

    tip_max2 = len(tips200)*12
    tip_count2 = 0

    def pick_up():
        nonlocal tip_count
        if tip_max == tip_count:
            m20.home()
            ctx.pause('Replace 20µl tipracks before resuming.')
            m20.reset_tipracks()
            tip_count = 0
        tip_count += 1
        m20.pick_up_tip()

    def pick_up2():
        nonlocal tip_count2
        if tip_max2 == tip_count2:
            m300.home()
            ctx.pause('Replace 200µl tipracks before resuming.')
            m300.reset_tipracks()
            tip_count2 = 0
        tip_count2 += 1
        m300.pick_up_tip()

    # ghost pickup to load and sense magnetic module to avoid crash
    pick_up()
    m20.move_to(magplate.wells()[0].top(3))

    # transfer samples
    if NUM_PLATES == 1:
        for s, d in zip(samples, dest):
            if not m20.hw_pipette['has_tip']:
                pick_up()
            m20.transfer(SAMPLE_VOL, s, d.bottom(), air_gap=2, new_tip='never')
            #m20.mix(3, 10, d)
            m20.drop_tip()

    elif NUM_PLATES == 2:
        for s, d in zip(samples, dest):
            if not m20.hw_pipette['has_tip']:
                pick_up()
            m20.transfer(SAMPLE_VOL, s, d.bottom(), air_gap=2, new_tip='never')
            #m20.mix(3, 10, d)
            m20.drop_tip()

        for s, d in zip(samples2, dest2):
            pick_up()
            m20.transfer(SAMPLE_VOL2, s, d.bottom(), air_gap=2, new_tip='never')
            #m20.mix(3, 10, d)
            m20.drop_tip()

    # transfer tris
    if NUM_PLATES == 1:
        for d in plate1.rows()[0][:NUM_SAMPLES]:
            pick_up2()
            m300.transfer(VOL_TRIS_1, tris, d.bottom(), air_gap=10, new_tip='never')
            m300.mix(3, MIX_VOLUME, d)
            m300.drop_tip()

    elif NUM_PLATES == 2:
        for d in plate1.rows()[0][:NUM_SAMPLES]:
            pick_up2()
            m300.transfer(VOL_TRIS_1, tris, d.bottom(), air_gap=10, new_tip='never')
            m300.mix(3, MIX_VOLUME, d)
            m300.drop_tip()

        for d in plate2.rows()[0][:NUM_SAMPLES]:
            pick_up2()
            m300.transfer(VOL_TRIS_2, tris, d.bottom(), air_gap=10, new_tip='never')
            m300.mix(3, MIX_VOLUME, d)
            m300.drop_tip()

