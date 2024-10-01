import mido
from lists import colors

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

def reset_pads(outport) -> None:
    for i in range(64):
        outport.send(write_led(i, colors["blank"]))
    pass

def enterProgrammerMode() -> mido.Message:
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 14, 1])

def exitProgrammerMode() -> mido.Message:
    return mido.Message('sysex', data=[0, 32, 41, 2, 13, 14, 0])

def list_ports() -> None:
    print(mido.get_input_names())
    print(mido.get_output_names())
