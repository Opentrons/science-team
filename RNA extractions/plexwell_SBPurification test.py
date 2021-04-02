#Sample Barcoding Purification Protocol 7/9
#Last update: January 6, 2021
#Seqwell Workflow

import math
from opentrons.types import Point

# metadata
metadata = {
    'protocolName': 'SeqWell - SB Purification',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.3'
}
NUM_PLATES = 1
NUM_SAMPLES = 96



def run(ctx):

    # load labware
    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magdeck', '6') #remember to change this back!
    mag_plate = magdeck.load_labware('nest_96_wellplate_2ml_deep')
    #mag_plate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')
    strips = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    res1 = ctx.load_labware(
        'nest_12_reservoir_15ml', '2', 'reagent reservoir 5')
    tipracks200 = [ctx.load_labware('opentrons_96_tiprack_300ul', slot)
                  for slot in ['7', '8']]
    tipracks300 = [ctx.load_labware('opentrons_96_filtertiprack_200ul', '9')]

    # pipettes
    m300 = ctx.load_instrument(
        'p300_multi_gen2', mount='left', tip_racks=tipracks200)
    p300 = ctx.load_instrument(
        'p300_single_gen2', mount='right', tip_racks=tipracks300)

    tip_count = 0
    tip_max = len(tipracks200)*12

    def pick_up():
        nonlocal tip_count
        if tip_count == tip_max:
            ctx.pause('Replace empty tipracks before resuming')
            m300.reset_tipracks()
            tip_count = 0
        tip_count += 1
        m300.pick_up_tip()

    # samples and reagents
    num_cols = math.ceil(NUM_SAMPLES/8)
    pooling_samples_strips = strips.columns()[:NUM_PLATES]
    num_mag_wells_per_set = math.ceil(NUM_SAMPLES/24)
    magwell_sets = [mag_plate.wells()[i*4:i*4+num_mag_wells_per_set]
                     for i in range(NUM_PLATES)]
    mag_samples_multi = mag_plate.rows()[0][:2]
    destination_tubes = strips.columns()[-1][:NUM_PLATES]

    magwise = res1.wells()[0]
    etoh = res1.wells()[1]
    waste = res1.wells()[-1]
    tris = res1.wells()[2]

    """ 4. SB Pool Purification """

    bead_vol = (850/96*NUM_SAMPLES)/len(magwell_sets[0])
    for m in mag_samples_multi:
        pick_up()
#        for _ in range(5):
#            m300.aspirate(200, magwise.bottom(2))
#            m300.dispense(200, magwise.bottom(15))
        m300.flow_rate.aspirate = 35
        m300.flow_rate.dispense = 10
        m300.flow_rate.blow_out = 150
#        m300.transfer(bead_vol, magwise, m, air_gap=20, new_tip='never',speed=50)
        m300.aspirate(bead_vol, magwise, rate=35)
        m300.move_to(magwise.bottom(10), speed=5)
        m300.dispense(bead_vol, m, rate=15)
        m300.flow_rate.aspirate = 100
        m300.flow_rate.dispense = 100
        m300.flow_rate.blow_out = 150
        #m300.mix(5, 200, m)
        #m300.flow_rate.aspirate = 35
        #m300.flow_rate.dispense = 10
        for _ in range(5):
            if _ == 4:
                m300.aspirate(200, m)
                m300.dispense(200, m,rate =1/20)
            else:
                m300.aspirate(200, m)
                m300.dispense(200, m)                        
        #m300.move_to(m.bottom(20),speed=1)
        #m300.aspirate(20,m.bottom(20))
        #m300.dispense(20,m.bottom(7),rate=1/10)
        m300.move_to(m.bottom(15),speed=1)
        ctx.delay(seconds=2)
        m300.blow_out()
        m300.drop_tip()

