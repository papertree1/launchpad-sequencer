import asyncio

class State():  
    def __init__(self, outport, sequencers) -> None:
        self.outport = outport
        self.sequencers = sequencers
        self.active_voice = 0
        self.tempo = 120

    def change_voice(self, voice_sel) -> None:
        self.active_voice = voice_sel

    async def draw_view(self) -> None:
        while True:
            #TODO Make it so that it isn't constantly updating
            self.sequencers[self.active_voice].view.draw()
            await asyncio.sleep(0.1)
