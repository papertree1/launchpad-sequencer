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
        self.active_view = sequencers[self.active_voice].view

    def change_voice(self, voice_sel) -> None:
        self.active_voice = voice_sel
        self.active_view = self.sequencers[self.active_voice].view

    def change_view(self, view_sel) -> None:
        self.active_view.set_view(view_sel)
        print("Changed view", self.active_voice, "to", self.active_view.view_type)
    
    def find_melodic(self) -> int:
        for i in range(len(self.sequencers)):
            if self.sequencers[i].isMelodic:
                return i
            
    def draw_view_live(self, previousColor):
        sequencer = self.sequencers[self.active_voice]
        step = sequencer.step
        seq_len = sequencer.length
        newColor = self.active_view.view[step]

        if self.active_steps[0] <= step < self.active_steps[1]:
            # Step is in the visible view
            self.active_view.change_color(step, "grey") # Draw the step bar
            if step != 0:
                self.active_view.change_color((step-1), previousColor) # Turn off last LED
        return newColor
        

    async def draw_view(self) -> None:
        while True:
            self.active_view.draw()
            await asyncio.sleep(0.1)
