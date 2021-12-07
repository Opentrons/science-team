from opentrons import protocol_api
import numpy as np
import requests
import uuid
from datetime import datetime
now = datetime.now()

testName = "P20 Water Calibration"

metadata = {
    'protocolName': 'Water and Pipette Calibration Test',
    'author': 'Anurag Kanase <anurag.kanase@opentrons.com>',
    'description': 'Loops through different volumes',
    'apiLevel': '2.9'
}

def run(protocol:protocol_api.ProtocolContext):
	#Intruments
	P20  = protocol.load_instrument('p20_single_gen2', 'right')
	P300 = protocol.load_instrument('p300_single_gen2', 'left')

	#Labware: Tipracks
	tip20  = protocol.load_labware('opentrons_96_tiprack_20ul', '1')
	tip200 = protocol.load_labware('opentrons_96_tiprack_300ul', '6')

	#Labware: Tubes and Plates
	plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '11')
	tubes = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '10')

	#Where's my Liquid
	water    = tubes['C1']
	glycerol = tubes['A1']
	plateLoc = plate['E5']

	#Volume Presets
	vol_p20  = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
	vol_p300 = [20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]

	#Parameter Setting
	startTip    = 'A1'
	tipPosition = 50 # Find the tip position in the scale
	AR 			= (1/95) * 95  # Change the later 95uL Aspiration Rate default
	MS			= (1/400)* 400 # Speed  
	date		= now.strftime("%b-%d")
	ipaddress	= 'http://169.254.109.198/update'

	liquid_calibration(water,'water',P20,'p20',tip20,vol_p20)
# cameraID = 1; # change the ID based on the camera chosen
# testName = param[1]
# pipetteName = param[2]
# liquidname = param[3]
# date = param[4]
# volume = param[5]
# uniqueID = param[6]
# processName = param[7]
# serialNo = param[8]
# testName+"/"+pipetteName+"/"+liquidname+"/"+date+"/"+processName
	def liquid_calibration(Liquid, liquidname, Pipette, pipetteName, Tiprack, Volumes, noofLoops=20,startTip,tipPosition):
		for vol in Volumes:
			lNo = 0
			for loop in range(5%noofLoops):
				lNo = lNo + 1
				Pipette.pick_up_tip(Tiprack[startTip])
				for internalloop in range(4):
					Pipette.aspirate(vol,Liquid.bottom(tipPosition-10), rate = AR)
					Pipette.move_to(Liquid.bottom(tipPosition+5), speed = MS)
					Pipette.move_to(plateLoc.top(30), )
					mkURL = testName + "/" + pipetteName + "/" + liquidname + "/" + date + "/" + "Aspiration/" + str(lNo) + "_" + str(uuid.uuid4()) + ".jpg"
					requests.post( ipaddress, json={'step': 'Capture', 'data':mkURL})
					Pipette.dispense(vol,Liquid.bottom(tipPosition+5), rate = MS)
					Pipette.blow_out()
				Pipette.drop_tip()

