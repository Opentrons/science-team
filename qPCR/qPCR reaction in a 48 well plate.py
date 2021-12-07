metadata = {'apiLevel': '2.0'}

# bright green — A1
# forward primer — A2
# reverse primer — A3
# water — A4
# super mastermix tube — B1
# control DNA — C1
# samples — D1 thru D6


def run(ctx):

    tuberack = ctx.load_labware(
        'opentrons_24_aluminumblock_nest_1.5ml_snapcap', '1')
    plate = ctx.load_labware('corning_384_wellplate_112ul_flat', '2')
    tips20 = ctx.load_labware('opentrons_96_tiprack_20ul', '4')
    tips300 = ctx.load_labware('opentrons_96_tiprack_300ul', '5')

    p20 = ctx.load_instrument('p20_single_gen2', 'right', tip_racks=[tips20])
    p300 = ctx.load_instrument('p300_single_gen2', 'left', tip_racks=[tips300])

    water = tuberack.wells_by_name()['A4']
    super_mm = tuberack.wells_by_name()['B1']
    control_dna = tuberack.wells_by_name()['C1']
    samples = tuberack.rows()[-1]

    for i, (r, vol) in enumerate(
            zip(tuberack.rows()[0][:4], [150, 9, 9, 102])):
        pip = p20 if vol < 20 else p300
        pip.pick_up_tip()
        pip.transfer(vol, r, super_mm.bottom(0.5), new_tip='never')
        pip.blow_out(super_mm.bottom(5))
        if i < 3:
            pip.drop_tip()

    p300.mix(10, 300, super_mm)
    p300.blow_out(super_mm.top(-5))
    p300.drop_tip()

    dests = [well for row in plate.rows()[:5:2] for well in row[:8]]
    p20.pick_up_tip()
    for d in dests:
        p20.transfer(9, super_mm, d, new_tip='never')
        p20.blow_out(d.top(-2))
    p20.drop_tip()

    sources = [control_dna] + [water] + samples
    dest_sets = [col[:5:2] for col in plate.columns()[:8]]

    for source, dest_set in zip(sources, dest_sets):
        for d in dest_set:
            p20.pick_up_tip()
            p20.aspirate(1, source)
            p20.aspirate(3, d)
            p20.dispense(4, d)
            p20.blow_out(d.top(-2))
            p20.drop_tip()
