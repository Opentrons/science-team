metadata = {
	'protocolName': 'temperature module',
	'author': 'Opentrons <protocols@opentrons.com>',
	'apiLevel': '2.4'
}

def run(ctx):

	tempdeck = ctx.load_module('Temperature Module Gen2', '1')
	tips300 = [ctx.load_labware('opentrons_96_tiprack_300ul', slot,
                                '200µl filtertiprack')
               for slot in ['4','7', '8', '10', '11']]
               
	# load P300M pipette
	m300 = ctx.load_instrument(
		'p300_multi_gen2', 'left', tip_racks=tips300)

	tempdeck.set_temperature(55)
	ctx.delay(minutes=30)
