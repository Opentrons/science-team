# metadata
metadata = {
    'protocolName': 'Tecan Cortisol Saliva ELISA',
    'author': 'Nick <protocols@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.0'
}


def run(ctx):

    # load labware
    reservoir = ctx.load_labware('nest_12_reservoir_15ml', '1')
    plate = ctx.load_labware('corning_96_wellplate_360ul_flat', '2')
    tipracks_s = ctx.load_labware('opentrons_96_tiprack_300ul', '3')
    reagent_plate = ctx.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '4')
    sample_tuberack = ctx.load_labware(
        'opentrons_15_tuberack_nest_15ml_conical', '5')
    # sample_tuberack = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    tipracks_m = [ctx.load_labware('opentrons_96_tiprack_300ul', slot)
                  for slot in ['6', '9']]

    # pipettes
    m300 = ctx.load_instrument(
        'p300_multi_gen2', 'left', tip_racks=tipracks_m)
    p300 = ctx.load_instrument(
        'p300_single_gen2', 'right', tip_racks=[tipracks_s])

    # sample and reagent setup
    samples_m = plate.rows()[0][:2]
    standards_controls = reagent_plate.rows()[0][0]
    enzyme_conjugate = reagent_plate.rows()[0][2:4]
    tmb_substrate_sol = reagent_plate.rows()[0][5:7]
    tmb_stop_sol = reagent_plate.rows()[0][8:10]
    wash_buffer = reservoir.wells()[:2]
    liquid_waste = [chan.top() for chan in reservoir.wells()[10:]]

    # transfer standards and controls
    m300.pick_up_tip()
    m300.transfer(50, standards_controls, plate.rows()[0][0], air_gap=20,
                  new_tip='never')
    m300.air_gap(20)
    m300.drop_tip()

    # transfer samples
    for d in plate.columns()[1]:
        p300.pick_up_tip()
        p300.transfer(50, sample_tuberack.wells()[8], d, air_gap=20,
                      new_tip='never')
        p300.air_gap(20)
        p300.drop_tip()

    # transfer enzyme conjugate
    for m, r in zip(samples_m, enzyme_conjugate):
        m300.pick_up_tip()
        m300.transfer(100, r, m, air_gap=20, new_tip='never')
        m300.blow_out(m.top(-2))
        m300.drop_tip()

    ctx.pause('Incubate 2 hours at RT (18-25°C) on an orbital shaker (400 – \
600 rpm).')

    # remove initial solution
    for m in samples_m:
        m300.pick_up_tip()
        m300.transfer(160, m.bottom(0.5), liquid_waste[0], air_gap=20, #change height for ELISA plate
                      new_tip='never')
        m300.air_gap(20)
        m300.drop_tip()

    # wash sequence
    tip_set = []
    tip_set.append(m300._next_available_tip()[-1])
    m300.pick_up_tip()
    tip_set.append(m300._next_available_tip()[-1])
    print(tip_set)
    for wash in range(4):
        if not m300.hw_pipette['has_tip']:
            m300.pick_up_tip(tip_set[0])
        m300.transfer(250, wash_buffer[wash//2], [m.top() for m in samples_m],
                      air_gap=20, new_tip='never')
        for m, tip in zip(samples_m, tip_set):
            if not m300.hw_pipette['has_tip']:
                m300.pick_up_tip(tip)
            m300.transfer(260, m.bottom(0.4), liquid_waste[wash//2], #change height for trough
                          air_gap=20, new_tip='never')
            m300.air_gap(20)
            if wash < 3:
                m300.drop_tip(tip)
            else:
                m300.drop_tip()

    # transfer TMB substrate solution
    for m, r in zip(samples_m, tmb_substrate_sol):
        m300.pick_up_tip()
        m300.transfer(100, r, m, air_gap=20, new_tip='never')
        m300.blow_out(m.top(-2))
        m300.drop_tip()

    ctx.pause('Incubate 30 minutes at RT (18-25°C) on an orbital shaker (400 \
– 600 rpm).')

    # transfer TMB stop solution
    for m, r in zip(samples_m, tmb_stop_sol):
        m300.pick_up_tip()
        m300.transfer(100, r, m, air_gap=20, new_tip='never')
        m300.blow_out(m.top(-2))
        m300.drop_tip()

    ctx.comment('Measure optical density with a photometer at 450 nm \
(Reference-wavelength: 600-650 nm) within 15 minutes after pipetting of the \
Stop Solution.')
