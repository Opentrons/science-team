# API 2
# Annika Yasuf
# Opentrons
metadata = {'apiLevel': '2.1'} 

COVER_TEMP = 105
PLATE_TEMP_PRE = 10
PLATE_TEMP_HOLD_1 = (94, 180)
PLATE_TEMP_HOLD_2 = (94, 10)
PLATE_TEMP_HOLD_3 = (70, 30)
PLATE_TEMP_HOLD_4 = (72, 30)
PLATE_TEMP_HOLD_5 = (72, 300)
PLATE_TEMP_POST = 4
CYCLES = 30


def run_temp_profile(thermocycler):
    # Set PRE temp
    thermocycler.set_block_temperature(PLATE_TEMP_PRE)
    # Set LID temp
    thermocycler.set_lid_temperature(COVER_TEMP)
    ## Close lid ######
    # thermocycler.close()
    # Set HOLD1 temp
    thermocycler.set_block_temperature(
        PLATE_TEMP_HOLD_1[0], PLATE_TEMP_HOLD_1[1])
    for i in range(CYCLES):
        # Set HOLD2 temp
        thermocycler.set_block_temperature(
            PLATE_TEMP_HOLD_2[0], PLATE_TEMP_HOLD_2[1])
        # Set HOLD3 temp
        thermocycler.set_block_temperature(
            PLATE_TEMP_HOLD_3[0], PLATE_TEMP_HOLD_3[1])
        # Set HOLD4 temp
        thermocycler.set_block_temperature(
            PLATE_TEMP_HOLD_4[0], PLATE_TEMP_HOLD_4[1])
    # Set HOLD5 temp
    thermocycler.set_block_temperature(
        PLATE_TEMP_HOLD_5[0], PLATE_TEMP_HOLD_5[1])
    thermocycler.deactivate_lid()
    # Set LAST temp
    thermocycler.set_block_temperature(PLATE_TEMP_POST)


def transfer_to_bottom_with_mix(pipette, volume, source, dest):
    pipette.pick_up_tip()
    pipette.aspirate(volume, source)
    pipette.dispense(volume, dest.bottom())
    pipette.mix(10, volume)
    pipette.drop_tip()


def run(context):
    tip_rack_200ul = context.load_labware_by_name(
        'opentrons_96_filtertiprack_200ul', '6')
    tip_rack_200ul_2 = context.load_labware_by_name(
        'opentrons_96_filtertiprack_200ul', '9')
    reagents = context.load_labware_by_name(
        'opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '3')
    thermocycler = context.load_module('thermocycler')
    tc_plate = thermocycler.load_labware('biorad_96_wellplate_200ul_pcr')

    # 96 samples
    # A1- F Primer 240ul Add 300ul total
    # B1- R Primer 240ul Add 300ul total
    # B3- Mastermix 6000ul 6050ul total
    # B4- Water 5040  6000ul total
    # A3- Empty 50ml eppendorf
    # C1- 480ul DNA 600ul total
    


    pipette300 = context.load_instrument('p300_single_gen2', 'right',
                                         tip_racks=[tip_rack_200ul, tip_rack_200ul_2])

    # Set PRE temp
    thermocycler.set_block_temperature(PLATE_TEMP_PRE)
    # Set LID temp
    thermocycler.set_lid_temperature(COVER_TEMP)


    # Forward Primer
    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('A1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        40,
        reagents.wells('A1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()



    # Reverse Primer

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        40,
        reagents.wells('B1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()


    # Mastermix

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B3'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()


    # water

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()
#50
    pipette300.pick_up_tip()
    pipette300.transfer(
        40,
        reagents.wells('B4'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()



    # DNA

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('C1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        200,
        reagents.wells('C1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    pipette300.pick_up_tip()
    pipette300.transfer(
        80,
        reagents.wells('C1'),
        reagents.wells('A3'),
        new_tip='never')
    pipette300.drop_tip()

    context.pause() #vortex full master mix tube


    well_names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
                  'D12', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']
    for well_name in well_names:
        # Should do: pick up tip from tiprack, aspirate 24 from tube, dispense into plate, mix 2x12, blow out, drop tip
        # def run(context):
        pipette300.transfer(
            100,
            reagents.wells('A3'),
            tc_plate.wells(well_name),
            trash=True,
            blow_out=True
        )

    context.pause()
    

   

    thermocycler.close_lid()
    run_temp_profile(thermocycler)
    thermocycler.open_lid()

    thermocycler.deactivate()
