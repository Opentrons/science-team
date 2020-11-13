#Reverse transcriptase PCR set up Protocol 1/9
#last edit: October 15, 2020
#Seqwell Workflow

import math

metadata = {
    'apiLevel': '2.3'
}

NUM_PLATES = 2 #number of plates, maximum of 2
NUM_SAMPLES = 96 #number of samples per plate


def run(ctx):
    rna_sample_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '1')
    rna_sample_plate2 = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2')

    tempdeck = ctx.load_module('temperature module gen2', '4')
    magdeck = ctx.load_module('magnetic module gen2', '6')

    mm_strips = tempdeck.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_20ul', slot)
              for slot in ['7', '8', '9', '10', '11']]
    tc_plate = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '3')
    tc_plate2 = ctx.load_labware(
        'biorad_96_wellplate_200ul_pcr', '5')

    m20 = ctx.load_instrument('p20_multi_gen2', 'left', tip_racks=tips20)

    magplate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    # reagents
    num_cols = math.ceil(NUM_SAMPLES/8)
    hex_dntp_mm_strip = mm_strips.columns()[0]
    rt_mm_strip = mm_strips.columns()[1]
    rt_mm_strip2 = mm_strips.columns()[2]
    rna_samples = rna_sample_plate.rows()[0][:num_cols]
    rna_samples2 = rna_sample_plate2.rows()[0][:num_cols]
    tc_samples = tc_plate.rows()[0][:num_cols]
    tc_samples2 = tc_plate2.rows()[0][:num_cols]

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

    # transfer sample to destination plate
    for s, d in zip(rna_samples, tc_samples):
        if not m20.hw_pipette['has_tip']:
            pick_up()
        m20.transfer(11, s, d, air_gap=2, new_tip='never')
        m20.air_gap(2)
        m20.drop_tip()

    if NUM_PLATES == 2:
        for s, d in zip(rna_samples2, tc_samples2):
            pick_up()
            m20.transfer(11, s, d, air_gap=2, new_tip='never')
            m20.air_gap(2)
            m20.drop_tip()


    # transfer from strip to destination and mix with sample
    for d in tc_samples:
        pick_up()
        m20.transfer(2, hex_dntp_mm_strip[0], d, air_gap=2, mix_after=(5, 10),
                     new_tip='never')
        m20.air_gap(2)
        m20.drop_tip()

    if NUM_PLATES == 2:
        for d in tc_samples2:
            pick_up()
            m20.transfer(2, hex_dntp_mm_strip[0], d, air_gap=2, mix_after=(5, 10),
                        new_tip='never')
            m20.air_gap(2)
            m20.drop_tip()

    ctx.pause('Take plate(s) out and run RT program on the thermocycler(s).')

    # transfer RT mastermix from strip to destination and mix
    for d in tc_samples:
        pick_up()
        m20.transfer(7, rt_mm_strip[0], d, air_gap=2, mix_after=(5, 10),
                     new_tip='never')
        m20.air_gap(2)
        m20.drop_tip()

    if NUM_PLATES == 2:
        for d in tc_samples2:
            pick_up()
            m20.transfer(7, rt_mm_strip2[0], d, air_gap=2, mix_after=(5, 10),
                        new_tip='never')
            m20.air_gap(2)
            m20.drop_tip()

    ctx.comment('Place plates in off deck thermocyclers \
    and run the RT reaction program ')
