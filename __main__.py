import mido
import asyncio
import types
import sys

import functions, views, lists
from state import State
from sequencer import Sequencer

DRUM_VOICES = 16
MELODIC_VOICES = 3
SEQUENCE_LENGTH = 8
TEMPO = 240

# Open MIDI Ports
inport = mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out")
outport = mido.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")
virtualOutport = mido.open_output("From MIDO", virtual=True)

def setupVoices(drumVoices: int, melVoices: int) -> list:
    # Create sequencers for drums and melodic voices
    global sequencers
    sequencers = []
    for i in range(drumVoices):
        seq = Sequencer(outport, virtualOutport)
        seq.length = SEQUENCE_LENGTH
        seq.view.set_view("SEQ_DRUMS")
        seq.voice = len(sequencers)
        seq.isMelodic = False
        seq.channel = 0 #All drums on the same channel
        sequencers.append(seq)
    for i in range(melVoices):
        seq = Sequencer(outport, virtualOutport)
        seq.length = SEQUENCE_LENGTH
        seq.view.set_view("SEQ_PUSH")
        seq.voice = len(sequencers)
        seq.isMelodic = True
        seq.channel = i + 1 #All voices on different cannels
        sequencers.append(seq)
    
    return sequencers

def _quit() -> None:
    outport.send(functions.exitProgrammerMode())
    functions.reset_pads(outport)
    virtualOutport.reset()
    sys.exit()

def make_stream():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)

    async def stream():
        while True:
            yield await queue.get()

    return callback, stream(), queue

async def process_messages(stream, state):
    pressedButtons = []
    async for message in stream:
        #print("message received:", message)
        if not (isinstance(message, types.GeneratorType) or isinstance(message, types.MethodType)) and message.type != 'sysex':
                type, ch, note, vel = functions.unpack_message(message)
                print("Message received:", type, ch, note, vel)
                if type == "control_change" and vel == 127:
                    #OUTSIDE BUTTONS
                    pressedButtons.append(note)
                    if len(pressedButtons) == 1:
                        #SINGLE BUTTON ACTIONS
                        match note:
                            case 19:
                                # Pause sequencers
                                for seq in sequencers:
                                    await seq.toggleSequencer(state.tempo)
                            case 29:
                                # Quit
                                _quit()
                            case 91:
                                # Change root note (melodic)
                                if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset += 1
                            case 92:
                                # Change root note (melodic)
                                if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset -= 1
                            case 93:
                                # Change active voice
                                state.change_voice(state.active_voice - 1)
                            case 94:
                                # Change active voice
                                state.change_voice(state.active_voice + 1)
                            case 95:
                                # Go to first melodic voice
                                state.change_voice(16)

                    else:
                        #MULTIPLE BUTTON ACTIONS
                        if 98 in pressedButtons and 19 in pressedButtons:
                            for seq in sequencers:
                                await seq.stopSequencer()
                elif type == "note_on" and vel == 127:
                    pressedButtons.append(note)
                    #GRID BUTTONS
                    if sequencers[state.active_voice].view.view_type == "SEQ_DRUMS":
                        #DRUM + SEQ LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            #SINGLE BUTTON ACTIONS
                            if 80 < note < 90:
                                # First row of sequencer #TODO Within sequencer
                                #TODO Play notes when clicking them
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(note)
                                active_sequencer.toggleNote(step)
                            elif note < 50 and note%10 <= 4:
                                # Change the active voice
                                state.active_voice = ((note % 10) - 1) + ((round(note / 10) - 1) * 4)
                                sequencers[state.active_voice].view.change_color(lists.leds.index(note), "light_blue")
                                print (state.active_voice)
                            elif 45 < note < 50:
                                pass #TODO Change view page
                        else:
                            #MULTIPLE BUTTON ACTIONS
                            if pressedButtons[0]%10 > 4: #TODO is this right?
                                # Change the velocity of the selected step
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(pressedButtons[1])
                                velocity = lists.leds.index(pressedButtons[0])
                                active_sequencer.velocities[step] = lists.velocities[pressedButtons[0]] # Change velocity
                                #active_sequencer.view.change_color(velocity, "purple_accent") # Change the color to reflect the velocity of the step

                    elif sequencers[state.active_voice].view.view_type == "SEQ_PUSH":
                        #KEYS + SEQ LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            if 80 < note < 90:
                                # First row of sequencer #TODO Within sequencer
                                #TODO Play notes when clicking them
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(note)
                                active_sequencer.toggleNote(step)
                        else:
                            #MULTIPLE BUTTON ACTIONS
                            if pressedButtons[0] < 40:
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(pressedButtons[1])
                                if active_sequencer.sequence[step] == 0:
                                    active_sequencer.toggleNote(step, lists.seq_and_push_keys[pressedButtons[0]])
                                else:
                                    active_sequencer.sequence[step] = lists.seq_and_push_keys[pressedButtons[0]]

                    elif sequencers[state.active_voice].view.view_type == "SEQ_FULL":
                        #64 STEP LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            #SINGLE BUTTON ACTIONS
                            active_sequencer = sequencers[state.active_voice]
                            step = lists.leds.index(note)
                            active_sequencer.toggleNote(step)

                elif vel == 0:
                    pressedButtons.remove(note)
                
if __name__ == "__main__":    
    async def main():
        print("READY!")
        cb, stream, queue = make_stream()

        mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out", callback=cb)

        outport.send(functions.enterProgrammerMode())
        drumVoices = DRUM_VOICES
        melVoices = MELODIC_VOICES
        state = State(outport, setupVoices(drumVoices, melVoices))
        state.tempo = TEMPO
        msg_loop_task = asyncio.create_task(process_messages(stream, state))
        sequencers[state.active_voice].initDraw()
        await state.draw_view()
        await msg_loop_task

    asyncio.run(main())

# Close MIDI port  
outport.send(mido.Message.from_bytes([0x90, 0x0C, 0x00]))
outport.close()