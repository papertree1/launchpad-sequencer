import functions
import mido as m

outport = m.open_output("Launchpad Mini MK3 LPMiniMK3 MIDI In")

outport.send(functions.enterProgrammerMode())
outport.send(functions.scroll_text(False, 10, 46, "Hello World"))
#outport.send(m.Message('sysex', data=[0, 32, 41, 2, 13, 7, 1, 7, 0, 37, 72, 101, 104, 104, 111, 32, 87, 111, 114, 104, 100]))
                                #data=(0, 32 ,41 ,2 ,13 ,7 ,0 ,0 ,4 ,46 ,72 ,101 ,108 ,108 ,111 ,32 ,87 ,111 ,114 ,108 ,100)