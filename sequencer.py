import asyncio
import mido

import functions, lists
from views import View

class Sequencer():
    def __init__(self, outport, virtualOutport) -> None:
        self.sequence = [0, 0, 0, 0, 0, 0, 0, 0,
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

    '''
    Runs the sequencer at tempo, with a length of steps
    '''
    async def runSequencer(self, tempo: int = 120) -> None:
        print(self.voice, "RUN")
        self.isRunning = True
        self.tempo = tempo
        self.tempo_s = 60 / self.tempo
        previousColor = self.view.view[self.step-1]

        while self.isRunning:
            #print(f'{self.voice} is running')
            newColor = self.view.view[self.step] # Get the color of the current step
            self.view.change_color(self.step, "grey") # Draw the step bar
            await self.sendNote(self.sequence[self.step]) #Send the corresponding note

            if self.step < self.length - 1:
                await self.sendNote(self.sequence[self.step - 1], velocity=0) # Turn off last note #TODO: tenir en compte length
                if self.step != 0:
                    self.view.change_color(self.step - 1, previousColor) # Turn off last LED
                await self._sleep()
                self.step += 1
            else: # Last step
                self.view.change_color(self.step - 1, previousColor) # Turn off last LED
                await self.sendNote(self.sequence[self.step - 1], velocity=0)
                await self._sleep()
                self.view.change_color(self.step, newColor) # Turn off last LED
                await self.sendNote(self.sequence[self.step], velocity=0)
                self.step = 0
            
            previousColor = newColor


    async def _sleep(self) -> None:
        await asyncio.sleep(self.tempo_s)

    async def pauseSequencer(self) -> None:
        print(self.voice, "PAUSE")
        self.isRunning = False
        await asyncio.sleep(0)

    async def toggleSequencer(self, tempo: int = 120) -> None:
        #print(self.voice, "TOGGLE")
        if self.isRunning:
            await self.pauseSequencer()
            self.run_task.cancel()
        else:
            self.run_task = asyncio.create_task(self.runSequencer(tempo))
        await asyncio.sleep(0)
    
    async def stopSequencer(self) -> None:
        print(self.voice, "STOP")
        self.isRunning = False
        self.view.view[self.step] = "blank"
        self.step = 0
        await asyncio.sleep(0)

    '''
    Sends a MIDI Note On message through a virtual port
    '''
    async def sendNote(self, note: int, velocity: int = 127) -> None:
        if note != 0:
            if self.isMelodic:
                self.virtualOutport.send(mido.Message('note_on', note=note, velocity=velocity, channel=self.channel))
            else:
                self.virtualOutport.send(mido.Message('note_on', note=lists.drumNotes[self.voice], velocity=velocity, channel=self.channel))
        await asyncio.sleep(0)

    def toggleNote(self, step) -> None:
        self.view.view[step] = "blank" if not self.sequence[step] == 0 else self.voice + 1
        self.sequence[step] = 0 if not self.sequence[step] == 0 else self.voice + 1

    def initDraw(self):
        for _ in range(self.length):
            self.view.view[_] = "blank" if self.sequence[_] == 0 else self.voice + 1
        self.view.draw()