import asyncio
'''
The State class contains all functions relating to the current state of the sequencer, a.k.a. what the Launchpad displays and responds to
'''
class State():  
    def __init__(self, outport, sequencers) -> None:
        self.outport = outport
        self.sequencers = sequencers
        self.active_voice = 0
        self.active_steps = [0, 32]
        self.tempo = 120

    def change_voice(self, voice_sel) -> None:
        self.active_voice = voice_sel
    
    def find_melodic(self) -> int:
        for i in range(len(self.sequencers)):
            if self.sequencers[i].isMelodic:
                return i

    async def draw_view(self) -> None:
        while True:
            self.sequencers[self.active_voice].view.draw()
            await asyncio.sleep(0.1)
