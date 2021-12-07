import serial

metadata = {
	'protocolName': 'BIoshake integration test',
	'author': 'Opentrons <protocols@opentrons.com>',
	'apiLevel': '2.4'
}

def run(ctx):
	plate_shake = ctx.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul', '3')


	#shake slow and heated at 70C for 2 minutes
	##change serial number when i get the bioshake!
	with serial.Serial('/dev/ttyUSB0', timeout=1) as ser:
		ser.write(b'tempOn\r')
		time.sleep(0.2)
		ser.write(b'setTempTarget700\r')
		time.sleep(0.2)
		ser.write(b'ssts500\r')
		time.sleep(0.2)
		ser.write(b'sonwr120\r')
		time.sleep(120)
		ser.write(b'soff\r')
#    time.sleep(0.2)
		ser.write(b'tempOff\r')
#    time.sleep(0.2)