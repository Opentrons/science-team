from opentrons.types import Point

metadata = {
    'protocolName': 'ELISA Protocol',
    'author': 'Rami Farawi <rami.farawi@opentrons.com>',
    'source': 'Custom Protocol Request',
    'apiLevel': '2.7'
}


def run(ctx):

    # load labware
    tiprack = [ctx.load_labware('opentrons_96_filtertiprack_200ul', '1')]
    samples = ctx.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2')
    elisa_plate = ctx.load_labware('lockwell_96_wellplate_360ul', '3')
    reagents = ctx.load_labware('nest_12_reservoir_15ml', '6')
    trash = ctx.load_labware('nest_1_reservoir_195ml', '9')

    # load instrument
    m300 = ctx.load_instrument('p300_multi_gen2', 'left', tip_racks=tiprack)

    # transfer samples to coated elisa plate
    col = elisa_plate.rows()[0][0]
    aspirate_loc = col.bottom().move(
            Point(x=(elisa_plate.wells()[0].diameter/2-1)))
    m300.pick_up_tip()
    m300.transfer(100,
                  samples.rows()[0][0],
                  col,
                  new_tip='never')
    m300.drop_tip()
    ctx.pause('''Add foil seal to Elisa plate. -
                 Place on bioshake set to 37C for one hour at 300 RPM.''')
    ctx.comment('\n')

    # move contents to trash before wash
    m300.pick_up_tip()
    m300.move_to(col.center())
    m300.aspirate(100, aspirate_loc)
    m300.dispense(100, trash.wells()[0].top())
    m300.drop_tip()
    ctx.comment('\n')

    # reagents
    ethanol = reagents.wells()[0:4]
    diluted_conjugate = reagents.wells()[5]
    substrate = reagents.wells()[7]

    # 3 ethanol washes
    for _ in range(3):
        m300.pick_up_tip()
        m300.aspirate(200, ethanol[0])
        m300.dispense(200, col)
        m300.move_to(col.center())
        m300.aspirate(200, aspirate_loc)
        m300.dispense(200, trash.wells()[0].top())
        m300.drop_tip()
    ctx.comment('\n')

    # add diluted diluted_conjugate
    m300.pick_up_tip()
    m300.aspirate(100, diluted_conjugate)
    m300.dispense(100, col)
    m300.drop_tip()
    ctx.comment('\n')

    ctx.pause('''Add foil seal to Elisa plate. -
                 Place on bioshake set to 37C for one hour at 300 RPM.''')

    # move contents to trash
    m300.pick_up_tip()
    m300.move_to(col.center())
    m300.aspirate(100, aspirate_loc)
    m300.dispense(100, trash.wells()[0].top())
    m300.drop_tip()
    ctx.comment('\n')

    # 3 ethanol washes
    for _ in range(3):
        m300.pick_up_tip()
        m300.aspirate(200, ethanol[1])
        m300.dispense(200, col)
        m300.move_to(col.center())
        m300.aspirate(200, aspirate_loc)
        m300.dispense(200, trash.wells()[0].top())
        m300.drop_tip()
    ctx.comment('\n')

    # add substrate
    m300.pick_up_tip()
    m300.aspirate(50, substrate)
    m300.dispense(50, col)
    m300.drop_tip()
    ctx.comment('\n')

    ctx.delay(minutes=15, msg='''Delaying for 15 minutes at room temperature.
                                 Please turn off lights''')

    # aspirate all remaining liquid
    m300.pick_up_tip()
    m300.move_to(col.center())
    m300.aspirate(50, aspirate_loc)
    m300.dispense(50, trash.wells()[0].top())
    m300.drop_tip()
    ctx.comment('\n')

    ctx.delay(minutes=15, msg='''Delaying for 15 minutes at 37C.
                                 Please turn off lights.''')
