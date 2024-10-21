import mido
import asyncio
import datetime

import functions
'''
inport = mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out")
outport = mido.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")
virtualOutport = mido.open_output("From MIDO", virtual=True)
'''
'''
async def play(note: int) -> None:
    virtualOutport.send(mido.Message('note_on', channel=0, note=note, velocity=0))
    await asyncio.sleep(0.5)
    virtualOutport.send(mido.Message('note_on', channel=0, note=note, velocity=127))
'''
'''
async def callback(i: int) -> None:
    print(i, datetime.datetime.now())
    await asyncio.sleep(i)
'''
def make_stream():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)

    async def stream():
        while True:
            yield await queue.get()

    return callback, stream()


async def print_messages(stream):
    # print messages as they come just by reading from stream
    async for message in stream:
        print("message recieved:", message)

if __name__ == "__main__":

    async def main():
        # create a callback/stream pair and pass callback to mido
        cb, stream = make_stream()

        outport = mido.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")
        inport = mido.open_input("Launchpad Mini MK3 LPMiniMK3 MIDI Out", callback=cb)

        
        outport.send(functions.enterProgrammerMode())
        msg_loop_task = asyncio.create_task(print_messages(stream))
        await msg_loop_task

    asyncio.run(main())


