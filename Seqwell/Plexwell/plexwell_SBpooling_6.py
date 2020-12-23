#Sample Barcoding Pooling Protocol 6/9
#last update: December 22, 2020
#Seqwell Workflow

import math
from opentrons.types import Point

# metadata
metadata = {
    'protocolName': 'Seqwell - SB Pooling',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.3'
}
NUM_PLATES = 1
NUM_SAMPLES = 96


def run(ctx):

    # load labware
    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')
    mag_plate = magdeck.load_labware('nest_96_wellplate_2ml_deep')
    # mag_plate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')
    strips = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    barcoded_plates = [
        ctx.load_labware('biorad_96_wellplate_200ul_pcr', slot,
                              'DNA plate ' + str(i+1))
        for i, slot in enumerate(['1', '2', '3', '5'][:NUM_PLATES])
    ]
    consolidation_tubes = ctx.load_labware(
        'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '7',
        'reagents microtuberack').wells()[:NUM_PLATES]

    tipracks20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
                  for slot in ['8', '10']]
    tipracks300 = [ctx.load_labware('opentrons_96_tiprack_300ul', '9')]

    # pipettes
    m20 = ctx.load_instrument(
        'p20_multi_gen2', mount='left', tip_racks=tipracks20)
    p300 = ctx.load_instrument(
        'p300_single_gen2', mount='right', tip_racks=tipracks300)

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
    barcoded_sample_sets_m = [
        plate.rows()[0][:num_cols] for plate in barcoded_plates]
    pooling_samples_strips = strips.columns()[:NUM_PLATES]
    num_mag_wells_per_set = math.ceil(NUM_SAMPLES/24)
    magwell_sets = [mag_plate.wells()[i*4:i*4+num_mag_wells_per_set]
                     for i in range(NUM_PLATES)]



    """ 3. SB Pooling (within plate) """
    for sample_set, strip, magwell_set, consol_tube in zip(
            barcoded_sample_sets_m, pooling_samples_strips, magwell_sets,
            consolidation_tubes):
        pick_up()
        for i, s in enumerate(sample_set):
            if m20.current_volume > 0:
                m20.dispense(m20.current_volume, s.top())
            m20.transfer(10.5, s, strip[0], air_gap=2,
                         new_tip='never')

        # slow flow rates for mixing
        m20.flow_rate.aspirate = 4
        m20.flow_rate.dispense = 4
        m20.flow_rate.blow_out = 4

        if i > 0:
            m20.mix(3, 10, strip[0])
        # reset to defaults
        m20.flow_rate.aspirate = 7.6
        m20.flow_rate.dispense = 7.6
        m20.flow_rate.blow_out = 7.6
        m20.air_gap(2)
        m20.blow_out()
        m20.drop_tip()

        vol_per_well = num_cols*9
        p300.consolidate(vol_per_well,
                         [well.bottom(0.5) for well in strip],
                         consol_tube.bottom())
        # divide into number of necessary magnetic wells
        vol_per_mag_well = (num_cols*9*8)/len(magwell_set)
        p300.transfer(vol_per_mag_well, consol_tube, magwell_set, air_gap=2)
