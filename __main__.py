import mido
import asyncio
import threading
import types
import sys

import functions, views, lists
from state import State
from sequencer import Sequencer

SEQUENCE_LENGTH = 8

#TODO Fix out of ranges 
#TODO 4-voice view
'''
TODO BUGS:
    - White light is on after pausing and playing, stays.
    - Transposition indicator stays when changing voice.
    - Keys doesn't draw sequence lights

'''
# Open MIDI Ports
inport = mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out")
outport = mido.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")
virtualOutport = mido.open_output("From MIDO", virtual=True)

'''
Creates the sequencers for drums and melodic voices
'''
def setupVoices(drumVoices: int, melVoices: int) -> list:
    # Create sequencers for drums and melodic voices
    global sequencers
    sequencers = []
    for i in range(drumVoices):
        seq = Sequencer(outport, virtualOutport)
        seq.length = SEQUENCE_LENGTH
        seq.view.set_view("SEQ_DRUMS", view=i)
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

'''
Quits the sequencer
'''
def _quit() -> None:
    outport.send(functions.exitProgrammerMode())
    virtualOutport.reset()
    sys.exit()

'''
Stop all notes
'''
def panic() -> None:
    virtualOutport.panic()
    
'''
Creates the stream that reads the incoming messages
'''
def make_stream():
    # Stream reads incoming messages,
    # callback puts messages in the queue
    # queue holds the messages
    # 
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)

    async def stream():
        while True:
            yield await queue.get()

    return callback, stream(), queue

'''
The main sequencer function. Processes messages and assigns functions to certain buttons and combinations.
'''
async def process_messages(stream, state):
    pressedButtons = []
    async for message in stream:
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
                                    await seq.toggleSequencer(state, state.tempo)
                            case 29:
                                # Quit
                                _quit()
                            case 39:
                                # Turn off all notes
                                panic()
                            case 91:
                                # Change root note (melodic)
                                if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset += 1
                                    functions.check_transposition(state)                                    
                            case 92:
                                # Change root note (melodic)
                                if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset -= 1
                                    functions.check_transposition(state)
                            case 93:
                                # Change active voice
                                state.change_voice(state.active_voice - 1)
                            case 94:
                                # Change active voice
                                state.change_voice(state.active_voice + 1)
                            case 95:
                                # Enter 4-voice view
                                print("h")
                                state.change_view("SEQ_FOUR")
                            case 96:
                                # Go to first drum voice
                                state.change_voice(0)
                            case 97:
                                # Go to first melodic voice
                                state.change_voice(state.find_melodic())

                    else:
                        #MULTIPLE BUTTON ACTIONS
                        if 89 in pressedButtons and 19 in pressedButtons:
                            # Stop sequencer
                            for seq in sequencers:
                                await seq.stopSequencer()
                        elif 89 in pressedButtons and 91 in pressedButtons:
                            # Change root by octave (melodic)
                            if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset += 12
                                    functions.check_transposition(state)
                        elif 89 in pressedButtons and 92 in pressedButtons:
                            # Change root by octave (melodic)
                            if sequencers[state.active_voice].isMelodic:
                                    sequencers[state.active_voice].offset -= 12
                                    functions.check_transposition(state)
                elif type == "note_on" and vel == 127:
                    pressedButtons.append(note)
                    #GRID BUTTONS
                    if sequencers[state.active_voice].view.view_type == "SEQ_DRUMS":
                        #DRUM + SEQ LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            #SINGLE BUTTON ACTIONS
                            if note > 50:
                                # Turn on/off notes
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(note)
                                active_sequencer.toggleNote(step)
                            elif note < 50 and note%10 <= 4:
                                # Change the active voice
                                state.active_voice = ((note % 10) - 1) + ((round(note / 10) - 1) * 4)
                                state.change_voice(state.active_voice)
                                await sequencers[state.active_voice].sendNote(1)
                                print (state.active_voice)
                            elif 45 <= note < 50:
                                print(note)
                                if note == 45:
                                    state.active_steps = [0, 32]
                                elif note == 46:
                                    state.active_steps = [33, 64]
                                elif note == 47:
                                    state.active_steps = [65, 96]
                                elif note == 48:
                                    state.active_steps = [97, 128]
                        else:
                            #MULTIPLE BUTTON ACTIONS
                            if 5 > pressedButtons[0]%10 > 4:
                                # Change the velocity of the selected step
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(pressedButtons[1])
                                active_sequencer.velocities[step] = lists.velocities[pressedButtons[0]] # Change velocity
                            elif 49 in pressedButtons:
                                # Change the active voice's sequence length
                                active_sequencer = sequencers[state.active_voice]
                                active_sequencer.length = lists.leds.index(pressedButtons[1]) + 1

                    elif sequencers[state.active_voice].view.view_type == "SEQ_PUSH":
                        #KEYS + SEQ LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            if note > 50:
                                # Turn on/off notes
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(note)
                                active_sequencer.toggleNote(step)
                        else:
                            #MULTIPLE BUTTON ACTIONS
                            if pressedButtons[0] < 40:
                                # Add/edit specific notes
                                active_sequencer = sequencers[state.active_voice]
                                step = lists.leds.index(pressedButtons[1])
                                if active_sequencer.sequence[step] == 0:
                                    active_sequencer.toggleNote(step, lists.seq_and_push_keys[pressedButtons[0]])
                                else:
                                    active_sequencer.sequence[step] = lists.seq_and_push_keys[pressedButtons[0]]
                            elif 49 in pressedButtons:
                                # Change the active voice's sequence length
                                active_sequencer = sequencers[state.active_voice]
                                active_sequencer.length = lists.leds.index(pressedButtons[1]) + 1

                    elif sequencers[state.active_voice].view.view_type == "SEQ_FULL":
                        #64 STEP LAYOUT MAPPINGS
                        if len(pressedButtons) == 1:
                            #SINGLE BUTTON ACTIONS
                            active_sequencer = sequencers[state.active_voice]
                            step = lists.leds.index(note)
                            active_sequencer.toggleNote(step)

                elif vel == 0 and note in pressedButtons:
                    pressedButtons.remove(note)

'''
Setup function. Initializes the state of the sequencer. Starts listening to messages
'''                
if __name__ == "__main__":    
    async def main():
        print("READY!")
        
        outport.send(functions.enterProgrammerMode())
        drumVoices, melVoices, tempo = await functions.initDraw(inport, outport)
        #melVoices = 0
        state = State(outport, setupVoices(drumVoices, melVoices))
        state.tempo = tempo

        cb, stream, queue = make_stream()
        #mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out", callback=cb) # Sends messages to the callback
        # Start MIDI input listener in a separate thread
        def midi_input_listener():
            with mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out", callback=cb):
                while True:
                    # Just keep the MIDI port open and trigger the callback when new messages come in
                    pass

        # Run MIDI input listener in a separate thread
        midi_input_thread = threading.Thread(target=midi_input_listener, daemon=True)
        midi_input_thread.start()

        msg_loop_task = asyncio.create_task(process_messages(stream, state))
        state.active_voice = 0
        await state.draw_view()

        await msg_loop_task

    asyncio.run(main())

# Close MIDI port  
outport.send(mido.Message.from_bytes([0x90, 0x0C, 0x00]))
outport.close()