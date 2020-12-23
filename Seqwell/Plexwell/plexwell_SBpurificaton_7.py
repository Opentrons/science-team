#Sample Barcoding Purification Protocol 7/9
#Last update: December 22, 2020
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
NUM_PLATES = 4
NUM_SAMPLES = 96



def run(ctx):

    # load labware
    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')
    mag_plate = magdeck.load_labware('nest_96_wellplate_2ml_deep')
    #mag_plate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')
    strips = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    res1 = ctx.load_labware(
        'usascientific_12_reservoir_22ml', '2', 'reagent reservoir 5')
    tipracks200 = [ctx.load_labware('opentrons_96_filtertiprack_200ul', slot)
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
    p300.flow_rate.aspirate = 10
    p300.flow_rate.dispense = 10
    p300.flow_rate.blow_out = 150

    bead_vol = (850/96*NUM_SAMPLES)/len(magwell_sets[0])
    for m in mag_samples_multi:
        pick_up()
        for _ in range(5):
            m300.aspirate(200, magwise.bottom(2))
            m300.dispense(200, magwise.bottom(15))
        m300.transfer(bead_vol, magwise, m, air_gap=20, new_tip='never')
        m300.mix(5, 200, m)
        m300.drop_tip()

    magdeck.engage()
    ctx.delay(minutes=5, msg='Incubating on magnet for 5 minutes.')

    vol_per_well = num_cols*9
    total_vol = (vol_per_well*8 + bead_vol)/len(magwell_sets[0])
    num_trans = math.ceil(total_vol/180)
    vol_per_trans = total_vol/num_trans

    p300.flow_rate.aspirate = 50
    p300.flow_rate.dispense = 50
    p300.flow_rate.blow_out = 150
    for m in mag_samples_multi:
        pick_up()
        for _ in range(num_trans):
            if m300.current_volume > 0:
                m300.dispense(p300.current_volume, m.top())
            m300.move_to(m.top())
            m300.transfer(vol_per_trans, m.bottom().move(Point(x=-3, y=1)),
                          waste, new_tip='never')
            m300.blow_out(waste)
            m300.air_gap(20)
        m300.drop_tip()

    p300.flow_rate.aspirate = 100
    p300.flow_rate.dispense = 100
    p300.flow_rate.blow_out = 150

    # etoh washes
    etoh_vol_per_magwell = 1600/len(magwell_sets[0])
    num_trans = math.ceil(etoh_vol_per_magwell/180)
    vol_per_trans = etoh_vol_per_magwell/num_trans
    for _ in range(2):
        for m in mag_samples_multi:
            pick_up()
            for _ in range(num_trans):
                if m300.current_volume > 0:
                    m300.dispense(p300.current_volume, etoh.top())
                m300.aspirate(vol_per_trans, etoh)
                m300.air_gap(20)
                m300.move_to(m.top())
                m300.dispense(vol_per_trans,
                              m.bottom().move(Point(x=-3, y=1)))
                m300.blow_out(m.top())
                m300.air_gap(20)
            m300.drop_tip()

        for m in mag_samples_multi:
            pick_up()
            for _ in range(num_trans):
                if m300.current_volume > 0:
                    m300.dispense(p300.current_volume, m.top())
                m300.move_to(m.top())
                m300.transfer(vol_per_trans,
                              m.bottom().move(Point(x=-3, y=1)), waste,
                              new_tip='never')
                m300.blow_out(waste.top())
                m300.air_gap(20)
            m300.drop_tip()

    ctx.delay(seconds=30, msg='Allowing beads to settle on magnet for 30 \
 seconds')
    magdeck.disengage()

    vol_tris = 40/len(magwell_sets[0]) if 40/len(magwell_sets[0]) > 20 else 20
    for m in mag_samples_multi:
        pick_up()
        m300.aspirate(vol_tris, tris)
        m300.air_gap(10)
        m300.move_to(m.top())
        loc = m.bottom().move(Point(x=3, y=1))
        m300.dispense(vol_tris+10, loc)
        m300.mix(10, 0.75*vol_tris, loc)
        m300.drop_tip()

    ctx.delay(minutes=5, msg='Incubating in Tris off magnet for 5 minutes.')
    magdeck.engage()
    ctx.delay(minutes=2, msg='Incubating on magnet for 2 minutes.')

    for magwell_set, dest in zip(magwell_sets, destination_tubes):
        p300.pick_up_tip()
        for m in magwell_set:
            p300.move_to(m.top())
            p300.aspirate(vol_tris, m.bottom().move(Point(x=-3, y=1)))
        p300.dispense(vol_tris*len(magwell_set), dest)
        p300.air_gap(10)
        p300.drop_tip()
