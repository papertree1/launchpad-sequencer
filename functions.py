import mido, asyncio
import sys
from lists import colors, drums, melodic
from views import View
'''
Create the needed MIDI ports for communicating with the Launchpad, as well as generating MIDI notes
'''
def setup_ports():
    inport = mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out")
    outport = mido.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")
    virtualOutport = mido.open_output("From MIDO2", virtual=True)
    return inport, outport, virtualOutport

'''
Unpacks an incoming message into variables
'''
def unpack_message(msg):
    if (msg.type != 'sysex'):
        type=''
        ch=note=vel=time=0
        msg = str(msg).split()
        type = msg[0]
        ch = int(msg[1].split('=')[1])
        note = int(msg[2].split('=')[1])
        vel = int(msg[3].split('=')[1])
        return type, ch, note, vel
    else:
        return 0, 0, 0, 0
'''
Indexes a 2D list using a single integer
'''
def index_2d(list, n):
    for i, x in enumerate(list):
        if n in x:
            return  (i, x.index(n))
   
'''
Changes the color of the LED following the documentation table:
https://fael-downloads-prod.focusrite.com/customer/prod/s3fs-public/downloads/Launchpad%20Mini%20-%20Programmers%20Reference%20Manual.pdf
'''
def write_led(led_id, color_vel, channel=0) -> mido.Message:
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 3, channel, led_id, color_vel])
'''
Displays scrolling text
'''
def scroll_text(looping: bool, speed: int, color: int, text: str) -> mido.Message:
    textAscii = list(text.encode('ascii'))
    message = mido.Message('sysex', data=[0, 32, 41, 2, 13, 7, 1 if looping else 0, speed, 0, color, *textAscii])
    return message
'''
Draws the first state of the sequencer
'''
async def initDraw(inport, outport):
    # Reset the board to start on a blank page
    for i in range(64):
        outport.send(write_led(i, 0))
    for i in range(9):
        outport.send(write_led(i + 91, 0)) # Reset top row
        outport.send(write_led(i*10 + 9, 0)) # Reset right row (9, 19, 29, ..., 89)
    # Draw the initial view, for selecting sequencer parameters
    initView = View(outport)
    initView.set_view("INIT")
    initView.draw()
    # Draw the leds on the right-most column, which the View class doesn't cover
    for i in range(8):
        if i > 4:
            outport.send(write_led(((i*10))+19, colors["yellow"]))
    drumVoices = 16
    meloVoices = 3
    bpm = 0
    '''
    outport.send(scroll_text(False, 15, colors["green"], "Drum Voices"))
    await asyncio.sleep(4)
    pressed = 0
    for msg in inport:
        type, ch, note, vel = unpack_message(msg)
        if type == 'note_on':
            if pressed == 0:
                drumVoices = note
                outport.send(scroll_text(False, 15, colors["light_blue"], "Melodic Voices"))
            elif pressed == 1:
                meloVoices = note
            elif pressed == 2:
                bpm = note * 10 #TODO fer be
            elif pressed > 2:
                break
            pressed += 1
    '''
    for msg in inport:
        type, ch, note, vel = unpack_message(msg)
        if type == 'note_on' or type == 'control_change':
            #print(note)
            if note > 60:
                #BPM Selection
                if 90 > note > 80:
                    #First row, 100ths
                    bpm = (bpm % 100) + (100*(note%10))
                    for i in range(9):
                        outport.send(write_led(81+i, colors["yellow"]))
                    outport.send(write_led(note, colors["grey"]))
                elif 80 > note > 70:
                    #Second row, 10ths:
                    bpm = (bpm//100 * 100) + (note%10)*10 + (bpm%10)
                    for i in range(9):
                        outport.send(write_led(71+i, colors["yellow"]))
                    outport.send(write_led(note, colors["grey"]))
                elif 70 > note > 60:
                    #Third row, 1s:
                    bpm = (bpm // 10) * 10 + (note%10)
                    for i in range(9):
                        outport.send(write_led(61+i, colors["yellow"]))
                    outport.send(write_led(note, colors["grey"]))
                print(bpm)
            elif note < 50:
                if note%10 < 5:
                    #Drum Voice selection
                    for i in range(16):
                        #Draw how many voices are selected
                        if i < drums[note]:
                            outport.send(write_led(list(drums.keys())[0+i], colors["green"]))
                        else:
                            outport.send(write_led(list(drums.keys())[0+i], colors["green_accent"]))
                    drumVoices = drums[note]
                    print(drumVoices)
                else:
                    #Melodic Voice selection
                    for i in range(16):
                        #Draw how many voices are selected
                        if i < melodic[note]:
                            outport.send(write_led(list(melodic.keys())[0+i], colors["blue"]))
                        else:
                            outport.send(write_led(list(melodic.keys())[0+i], colors["light_blue"]))
                    meloVoices = melodic[note]
                    print(meloVoices)
            elif note == 54 or note == 55:
                #Confirm, exit
                for i in range(8):
                    if i > 4:
                        outport.send(write_led(((i*10))+19, colors["blank"]))
                break
            elif note == 51 or note == 58:
                #Cancel, exit
                reset_pads(outport)
                outport.send(exitProgrammerMode())
                sys.exit()


    #self.view.draw()
    return [drumVoices, meloVoices, bpm if bpm != 0 else 120]
'''
Resets all the pads to their default state, without any light
'''
def reset_pads(outport) -> None:
    for i in range(64):
        outport.send(write_led(i, colors["blank"]))
    pass
'''
Sets the Launchpad in Programmer Mode, which gives access to Programmer functions
'''
def enterProgrammerMode() -> mido.Message:
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 14, 1])
'''
Sets the Launchpad in Live Mode, its default
'''
def exitProgrammerMode() -> mido.Message:
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 14, 0])
'''
Prints the available MIDI inputs and outputs
'''
def list_ports() -> None:
    print(mido.get_input_names())
    print(mido.get_output_names())