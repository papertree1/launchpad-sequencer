import asyncio
import mido

import functions, lists
from views import View, seq_and_push

'''
The Sequencer class contains all functions relating the usage of the sequencers, as well as the sequence itself
'''
class Sequencer():
    def __init__(self, outport, virtualOutport) -> None:
        self.sequence =   [0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0]
        self.velocities = [0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0, 0, 0]
        self.step = 0
        self.voice = 1
        self.length = 8
        self.isMelodic = True
        self.isRunning = False
        self.channel = 0
        self.outport = outport
        self.virtualOutport = virtualOutport
        self.view = View(self.outport)
        self.offset = 0
        self.tempo = 120
        self.tempo_s = 0
    '''
    Runs the sequencer at tempo, with a length of steps
    '''
    async def runSequencer(self, state, tempo: int = 120) -> None:
        print(self.voice, "RUN")
        self.isRunning = True
        self.tempo = tempo
        self.calculateTempo(state)
        previousColor = self.view.view[(self.step-1)%self.length]

        while self.isRunning:
            #print(f'{self.voice} is running')
            if self.voice == state.active_voice:
                # Draw the sequence if the sequencer is active
                newColor = state.draw_view_live(previousColor)
                previousColor = newColor
            '''
            newColor = self.view.view[self.step%self.length] # Get the color of the current step
            if state.active_steps[0] <= self.step < state.active_steps[1]:
                self.view.change_color((self.step%self.length), "grey") # Draw the step bar
            if self.isMelodic:
                self.drawNotes()
            else:
                self.drawVelocity()
            '''
            
            # Play the note
            note = self.sequence[self.step] + self.offset if self.sequence[self.step] != 0 else 0
            await self.sendNote(note, self.velocities[self.step]) # Send the corresponding note
            await self.sendNote(self.sequence[(self.step-1)%self.length], velocity=0) # Turn off last note

            await self._sleep()

            if self.step < self.length - 1:
                self.step += 1
            else: # Last step
                self.step = 0

    '''
    Pauses the sequencer for the time set by the tempo
    '''
    async def _sleep(self) -> None:
        await asyncio.sleep(self.tempo_s)
    '''
    Pauses the sequencer
    '''
    async def pauseSequencer(self) -> None:
        print(self.voice, "PAUSE")
        self.isRunning = False
        await asyncio.sleep(0)
    '''
    Toggles on(play) or off(pause) the sequencer
    '''
    async def toggleSequencer(self, state, tempo: int = 120) -> None:
        #print(self.voice, "TOGGLE")
        if self.isRunning:
            self.outport.send(functions.write_led(19, 0, 2)) # Stop flashing red
            await self.pauseSequencer()
            self.run_task.cancel()
        else:
            self.outport.send(mido.Message('note_on', channel=1, note=19, velocity=5)) # Flashing red when playing
            self.run_task = asyncio.create_task(self.runSequencer(state, tempo))
        await asyncio.sleep(0)
    '''
    Stops and resets the sequencer
    '''
    async def stopSequencer(self) -> None:
        print(self.voice, "STOP")
        self.isRunning = False
        self.view.view[self.step] = "blank" # Delete step bar
        self.step = 0
        await asyncio.sleep(0)

    def calculateTempo(self, state) -> None:
        self.tempo = state.tempo
        self.tempo_s = 60 / self.tempo
    '''
    Sends a MIDI Note On message through a virtual port
    '''
    async def sendNote(self, note: int, velocity: int = 127) -> None:
        #if velocity != 0:
        if note != 0:
            if self.isMelodic:
                self.virtualOutport.send(mido.Message('note_on', note=note, velocity=velocity, channel=self.channel))
            else:
                self.virtualOutport.send(mido.Message('note_on', note=lists.drumNotes[self.voice], velocity=velocity, channel=self.channel))
        
        await asyncio.sleep(0)
    '''
    Turns notes on or off, as well as the corresponding led
    '''
    def toggleNote(self, step, note=60) -> None:
        if self.sequence[step] != 0:
            # Turn note off
            self.view.view[step] = "blank"
            self.velocities[step] = 0
            if self.isMelodic:
                self.sequence[step] = 0 #Default note is C4
            else:
                self.sequence[step] = 0
        else:
            # Turn note on
            self.view.view[step] = self.voice + 1
            self.velocities[step] = 127
            if self.isMelodic:
                self.sequence[step] = note
            else:
                self.sequence[step] = self.voice + 1
    '''
    Reflects the velocity of the current step in the velocity grid
    '''
    def drawVelocity(self):
        step_vel = self.velocities[self.step]
        for i in range(len(self.view.view)):
            if i > 40 and i%8 >= 4:
                #Within velocity spaces
                if self.view.view[i] == "purple_accent":
                    self.view.change_color(i, "purple")
        if step_vel != 0:
            index = list(lists.velocities.values()).index(step_vel)
            value = list(lists.velocities.keys())[index]
            led = lists.leds.index(value)
            self.view.change_color(led, "purple_accent")
    '''
    Reflects the note of the current step in the note grid
    '''
    def drawNotes(self):
        step_note = self.sequence[self.step]
        for i in range(len(self.view.view)):
            if i > 40:
                if self.view.view[i] == "green_accent":
                    self.view.change_color(i, seq_and_push()[i])
        if step_note != 0:
            values = []
            i=0
            for val in lists.seq_and_push_keys.values():
                if val == step_note:
                    values.append(i)
                i+=1
            keys = []
            for val in values:
                keys.append(list(lists.seq_and_push_keys.keys())[val])
            leds = []
            for i in range(len(lists.leds)):
                if lists.leds[i] in keys:
                    leds.append(lists.leds.index(lists.leds[i]))
            for led in leds:
                self.view.change_color(led, "green_accent")