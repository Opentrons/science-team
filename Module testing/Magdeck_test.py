metadata = {'apiLevel': '2.3'} 


def run(protocol_context):
# Module Setup
    magdeck = protocol_context.load_module('magdeck', '6')
    mag_plate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    magdeck.disengage()

    MAG_HEIGHT = 13.7

# Place samples on the magnets
    magdeck.engage(height=MAG_HEIGHT)                                                                                                                                                                                                           


    
