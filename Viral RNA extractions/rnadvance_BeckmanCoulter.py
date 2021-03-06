from opentrons.types import Point
import json
import os
import math
import threading
from time import sleep

metadata = {
    'protocolName': 'Beckman RNadvance Viral XP',
    'author': '',
    'apiLevel': '2.3'
}


"""
Here is where you can define the parameters of your protocol:

NUM_SAMPLES: Number of samples to process in columns of 8 (1-96). The protocol will round up to the nearest column.
STARTING_VOL: Volume of sample + lysis buffer + internal controls + proteinase K (in µl) that will be removed initially (after bead addition).
ELUTION_VOL: Volume of final elution that will be transferred to a fresh PCR Plate at the end of the protocol (to be passed to qPCR assay).
TIP_TRACK: If True, will pick up tips starting after the last accessed up tip from the previous run. If False, will start at the first tip of the first tiprack.
PARK: If True, will store tips in a designated rack between reagent addition and supernatant removal. If False, will dispose tips after each step.
FLASH: If True, will flash lights if liquid waste or tip waste needs to be disposed of
"""

NUM_SAMPLES = 24
STARTING_VOL = 400
ELUTION_VOL = 40
TIP_TRACK = False
PARK = True
FLASH = False


# Definitions for deck light flashing
class CancellationToken:
    def __init__(self):
       self.is_continued = False

    def set_true(self):
       self.is_continued = True

    def set_false(self):
       self.is_continued = False


def turn_on_blinking_notification(hardware, pause):
    while pause.is_continued:
        hardware.set_lights(rails=True)
        sleep(1)
        hardware.set_lights(rails=False)
        sleep(1)


def create_thread(ctx, cancel_token):
    t1 = threading.Thread(target=turn_on_blinking_notification, args=(ctx._hw_manager.hardware, cancel_token))
    t1.start()
    return t1


# Start protocol
def run(ctx):
    # Setup for flashing lights notification to empty trash
    cancellationToken = CancellationToken()

    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    magdeck = ctx.load_module('magdeck', '3')
    magdeck.disengage()
    magheight = 13.7
    #magheight = 6.8
    magplate = magdeck.load_labware('nest_96_wellplate_2ml_deep')
    # magplate = magdeck.load_labware('biorad_96_wellplate_200ul_pcr')
    tempdeck = ctx.load_module('Temperature Module Gen2', '1')
    flatplate = tempdeck.load_labware(
                'opentrons_96_aluminumblock_nest_wellplate_100ul',)
    waste = ctx.load_labware('nest_1_reservoir_195ml', '6',
                             'Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware(
        'nest_12_reservoir_15ml', '2', 'reagent reservoir 1')
    num_cols = math.ceil(NUM_SAMPLES/8)
    tips300 = [ctx.load_labware('opentrons_96_tiprack_300ul', slot, '200µl filtertiprack')
               for slot in ['4', '7', '8', '9', '10', '11']]
    if PARK:
        parkingrack = ctx.load_labware(
            'opentrons_96_tiprack_300ul', '5', 'empty tiprack for parking')
        all_spots = [well for rack in [parkingrack] + tips300 for well in rack.rows()[0]]
        parking_spot_sets = [all_spots[i*num_cols:i*num_cols+num_cols] for i in range(5)]
    else:
        tips300.insert(0, ctx.load_labware('opentrons_96_tiprack_300ul', '5',
                                           '200µl filtertiprack'))
        parking_spots = [None for none in range(12)]


    # load P300M pipette
    m300 = ctx.load_instrument(
        'p300_multi_gen2', 'left', tip_racks=tips300)

    """
    Here is where you can define the locations of your reagents.
    """
    binding_buffer = res1.wells()[:2]
    etoh1 = res1.wells()[2:6]
    etoh2 = res1.wells()[6:10]
    elution_solution = res1.wells()[-1]

    mag_samples_m = magplate.rows()[0][:num_cols]
    elution_samples_m = flatplate.rows()[0][:num_cols]

#    magdeck.disengage()  # just in case
    #tempdeck.set_temperature(4)

    m300.flow_rate.aspirate = 300
    m300.flow_rate.dispense = 300
    m300.flow_rate.blow_out = 300

    folder_path = '/data/B'
    tip_file_path = folder_path + '/tip_log.json'
    tip_log = {'count': {}}
    if TIP_TRACK and not ctx.is_simulating():
        if os.path.isfile(tip_file_path):
            with open(tip_file_path) as json_file:
                data = json.load(json_file)
                if 'tips300' in data:
                    tip_log['count'][m300] = data['tips300']
                else:
                    tip_log['count'][m300] = 0
        else:
            tip_log['count'][m300] = 0
    else:
        tip_log['count'] = {m300: 0}

    tip_log['tips'] = {
        m300: [tip for rack in tips300 for tip in rack.rows()[0]]}
    tip_log['max'] = {m300: len(tip_log['tips'][m300])}

    def _pick_up(pip, loc=None):
        nonlocal tip_log
        if tip_log['count'][pip] == tip_log['max'][pip] and not loc:
            ctx.pause('Replace ' + str(pip.max_volume) + 'µl tipracks before \
resuming.')
            pip.reset_tipracks()
            tip_log['count'][pip] = 0
        if loc:
            pip.pick_up_tip(loc)
        else:
            pip.pick_up_tip(tip_log['tips'][pip][tip_log['count'][pip]])
            tip_log['count'][pip] += 1

    switch = True
    drop_count = 0
    drop_threshold = 120  # number of tips trash will accommodate before prompting user to empty

    def _drop(pip):
        nonlocal switch
        nonlocal drop_count
        side = 30 if switch else -18
        drop_loc = ctx.loaded_labwares[12].wells()[0].top().move(
            Point(x=side))
        pip.drop_tip(drop_loc)
        switch = not switch
        drop_count += 8
        if drop_count == drop_threshold:
            # Setup for flashing lights notification to empty trash
            if FLASH:
                if not ctx._hw_manager.hardware.is_simulator:
                    cancellationToken.set_true()
                # thread = create_thread(ctx, cancellationToken)
            m300.home()
            ctx.pause('Please empty tips from waste before resuming.')

            ctx.home()  # home before continuing with protocol
            if FLASH:
                cancellationToken.set_false()  # stop light flashing after home
                # thread.join()

            drop_count = 0

    waste_vol = 0
    waste_threshold = 185000

    def remove_supernatant(vol, set_ind, park=False):
        """
        `remove_supernatant` will transfer supernatant from the deepwell
        extraction plate to the liquid waste reservoir.
        :param vol (float): The amount of volume to aspirate from all deepwell
                            sample wells and dispense in the liquid waste.
        :param park (boolean): Whether to pick up sample-corresponding tips
                               in the 'parking rack' or to pick up new tips.
        """

        def _waste_track(vol):
            nonlocal waste_vol
            if waste_vol + vol >= waste_threshold:
                # Setup for flashing lights notification to empty liquid waste
                if FLASH:
                    if not ctx._hw_manager.hardware.is_simulator:
                        cancellationToken.set_true()
                    # thread = create_thread(ctx, cancellationToken)
                m300.home()
                ctx.pause('Please empty liquid waste (slot 11) before resuming.')

                ctx.home()  # home before continuing with protocol
                if FLASH:
                    cancellationToken.set_false() # stop light flashing after home
                    # thread.join()

                waste_vol = 0
            waste_vol += vol

        m300.flow_rate.aspirate = 30
        num_trans = math.ceil(vol/200)
        vol_per_trans = vol/num_trans
        for i, (m, spot) in enumerate(zip(mag_samples_m, parking_spot_sets[set_ind])):
            if park:
                _pick_up(m300, spot)
            else:
                _pick_up(m300)
            side = -1 if i % 2 == 0 else 1
            loc = m.bottom(0.5).move(Point(x=side*2))
            for _ in range(num_trans):
                _waste_track(vol_per_trans)
                if m300.current_volume > 0:
                    m300.dispense(m300.current_volume, m.top())  # void air gap if necessary
                m300.move_to(m.center())
                m300.transfer(vol_per_trans, loc, waste, new_tip='never',
                              air_gap=20)
                #m300.blow_out(waste)
                m300.air_gap(20)
            _drop(m300)
        m300.flow_rate.aspirate = 150

    def bind(vol, set_ind=0, park=True):
        """
        `bind` will perform magnetic bead binding on each sample in the
        deepwell plate. Each channel of binding beads will be mixed before
        transfer, and the samples will be mixed with the binding beads after
        the transfer. The magnetic deck activates after the addition to all
        samples, and the supernatant is removed after bead bining.
        :param vol (float): The amount of volume to aspirate from the elution
                            buffer source and dispense to each well containing
                            beads.
        :param park (boolean): Whether to save sample-corresponding tips
                               between adding elution buffer and transferring
                               supernatant to the final clean elutions PCR
                               plate.
        """

        # add bead binding buffer and mix samples
        for i, (well, spot) in enumerate(zip(mag_samples_m, parking_spot_sets[set_ind])):
            source = binding_buffer[i//(12//len(binding_buffer))]
            if park:
                _pick_up(m300, spot)
            else:
                _pick_up(m300)
    #        for _ in range(3):
    #           m300.aspirate(180, source.bottom(0.5))
    #            m300.dispense(180, source.bottom(5))
            num_trans = math.ceil(vol/210)
            vol_per_trans = vol/num_trans
            for t in range(num_trans):
                if m300.current_volume > 0:
                    m300.dispense(m300.current_volume, source.top())  # void air gap if necessary
                m300.transfer(vol_per_trans, source, well.top(), air_gap=20,
                              new_tip='never')
                if t == 0:
                    m300.air_gap(20)
            m300.mix(5, 200, well)
            #m300.blow_out(well.top(-2))
            m300.air_gap(20)
            if park:
                m300.drop_tip(spot)
            else:
                _drop(m300)

        ctx.delay(minutes=5, msg='Incubating off MagDeck for 5 minutes.')
        magdeck.engage(height=magheight)
        ctx.delay(minutes=5, msg='Incubating on MagDeck for 5 minutes.')

        # remove initial supernatant
        remove_supernatant(vol+STARTING_VOL, set_ind=set_ind, park=park)

    def wash(vol, source, set_ind, mix_reps=15, park=True, resuspend=True):
        """
        `wash` will perform bead washing for the extraction protocol.
        :param vol (float): The amount of volume to aspirate from each
                            source and dispense to each well containing beads.
        :param source (List[Well]): A list of wells from where liquid will be
                                    aspirated. If the length of the source list
                                    > 1, `wash` automatically calculates
                                    the index of the source that should be
                                    accessed.
        :param mix_reps (int): The number of repititions to mix the beads with
                               specified wash buffer (ignored if resuspend is
                               False).
        :param park (boolean): Whether to save sample-corresponding tips
                               between adding wash buffer and removing
                               supernatant.
        :param resuspend (boolean): Whether to resuspend beads in wash buffer.
        """

        if resuspend and magdeck.status == 'engaged':
            magdeck.disengage()

        num_trans = math.ceil(vol/200)
        vol_per_trans = vol/num_trans
        for i, (m, spot) in enumerate(zip(mag_samples_m, parking_spot_sets[set_ind])):
            _pick_up(m300)
            side = 1 if i % 2 == 0 else -1
            loc = m.bottom(0.5).move(Point(x=side*2))
            src = source[i//(12//len(source))]
            for n in range(num_trans):
                if m300.current_volume > 0:
                    m300.dispense(m300.current_volume, src.top())
                m300.transfer(vol_per_trans, src, m.top(), air_gap=20,
                              new_tip='never')
                if n < num_trans - 1:  # only air_gap if going back to source
                    m300.air_gap(20)
            if resuspend:
                m300.mix(mix_reps, 150, loc)
            # m300.blow_out(m.top())
            m300.air_gap(20)
            if park:
                m300.drop_tip(spot)
            else:
                _drop(m300)

        if magdeck.status == 'disengaged':
            magdeck.engage(height=magheight)
        minutes = 2 if resuspend else 5
        ctx.delay(minutes=minutes, msg='Incubating on MagDeck for \
' + str(minutes) + ' minutes.')

        remove_supernatant(vol, set_ind=set_ind, park=park)

    def elute(vol, set_ind, park=True):
        """
        `elute` will perform elution from the deepwell extraciton plate to the
        final clean elutions PCR plate to complete the extraction protocol.
        :param vol (float): The amount of volume to aspirate from the elution
                            buffer source and dispense to each well containing
                            beads.
        :param park (boolean): Whether to save sample-corresponding tips
                               between adding elution buffer and transferring
                               supernatant to the final clean elutions PCR
                               plate.
        """

        # resuspend beads in elution
        if magdeck.status == 'enagaged':
            magdeck.disengage()
        for i, (m, spot) in enumerate(zip(mag_samples_m, parking_spot_sets[set_ind])):
            _pick_up(m300)
            side = 1 if i % 2 == 0 else -1
            loc = m.bottom(0.5).move(Point(x=side*2))
            m300.aspirate(vol, elution_solution)
            m300.move_to(m.center())
            m300.dispense(vol, loc)
            m300.mix(10, 0.8*vol, loc)
            m300.blow_out(m.bottom(5))
            m300.air_gap(20)
            if park:
                m300.drop_tip(spot)
            else:
                _drop(m300)

        ctx.delay(minutes=5, msg='Incubating off magnet at room temperature \
for 5 minutes')
        magdeck.engage(height=magheight)
        ctx.delay(minutes=2, msg='Incubating on magnet at room temperature \
for 2 minutes')

        for i, (m, e, spot) in enumerate(
                zip(mag_samples_m, elution_samples_m, parking_spot_sets[set_ind])):
            if park:
                _pick_up(m300, spot)
            else:
                _pick_up(m300)
            side = -1 if i % 2 == 0 else 1
            loc = m.bottom(0.5).move(Point(x=side*2))
            m300.transfer(vol, loc, e.bottom(5), air_gap=20, new_tip='never')
            #m300.blow_out(e.top(-2))
            m300.air_gap(20)
            m300.drop_tip()

    """
    Here is where you can call the methods defined above to fit your specific
    protocol. The normal sequence is:
    - bind(200)
    - wash(500, wash1)
    - wash(500, wash2)
    - wash(500, wash3)
    - elute(50)
    """
    bind(350, set_ind=0, park=PARK)
    wash(400, etoh1, set_ind=1, mix_reps=10, park=PARK)
    wash(400, etoh2, set_ind=2, mix_reps=10, park=PARK)
    ctx.delay(minutes=2, msg='Dry beads')
    elute(40, set_ind=3, park=PARK)
