import sys
sys.path.append('/var/lib/jupyter/notebooks')
from QOT import QIDevice
from opentrons import protocol_api

metadata = {
    'protocolName': 'Bioshake 3000T Elm testing',
    'description': 'testing Qinstruments Bioshake 3000T Elm on the OT-2',
    'apiLevel': '2.8'
}

def run(protocol: protocol_api.ProtocolContext):
	#load tip rack, pipette and labware
    tip_rack = protocol.load_labware('opentrons_96_tiprack_300ul', 2)

    pipette_right = protocol.load_instrument('p300_single', 
                                             'right', tip_racks=[tip_rack])

    #load bioshake - remember to change serial number to match your devices!
    device = QIDevice(serial_number='19762', 
                      deck_position=1, adapter_set_up=1, protocol=protocol)
    
    #first, upload Qinstrument's custom labware to the OT-2. Next, make sure you
    #add the z_offset, item_depth, and item_volume
    lbw = device.load_labware( '2016_1062',
    							z_offset=   (11,   5),
                                item_depth= (37.5, 30),
                                item_volume=(1500, 500))
    #resetting bioshake just in case
    device.exec_cmd('resetDevice')

    #teseting pipette
    pipette_right.pick_up_tip()
    pipette_right.aspirate(100, lbw['AA1'])
    pipette_right.dispense(100, lbw['AA5'])
    pipette_right.drop_tip()

    #testing temp at 37C for 20 seconds while shaking still occurs
    device.exec_cmd('setShakeTargetSpeed500')  
    device.exec_cmd('shakeOn')  
    device.exec_cmd('setTempTarget370', blocking=True)
    device.exec_cmd('tempOn', polling=True)
    protocol.delay(seconds=20, msg='shaking at 500rpm and heating at 37C for 20 seconds')
    device.exec_cmd('shakeOff')

    #testing pipette with temperature on
    pipette_right.pick_up_tip()
    pipette_right.aspirate(100, lbw['AA2'])
    pipette_right.dispense(100, lbw['AA3'])
    pipette_right.drop_tip()

    device.exec_cmd('tempOff')

    protocol.comment('Protocol complete.')