from lists import leds, colors
import functions
import mido
import time as t
import math
'''
The View class contains all functions relating to views and drawing modes, as well as the setup for each different type.
A View is defined as a 8x8 grid, corresponding to the pads on the launchpad that send a 'Note On' message.
'''
class View():
    def __init__(self, outport: mido.ports) -> None:
        self.view = empty_view()
        self.outport = outport

    def draw(self) -> None:
        for i, square in enumerate(self.view):
            square = square%16 if isinstance(square, int) else square
            self.outport.send(functions.write_led(leds[i], colors[square]))
    
    def set_view(self, view_sel) -> None:
        views = {
            "SEQ_DRUMS": seq_and_drums(),
            "SEQ_KEYBOARD": seq_and_keyboard(),
            "SEQ_FULL": seq_full(),
            "SEQ_FOUR": seq_four(), #TODO Opció per a canviar les veus individualment
            "SEQ_PUSH": seq_and_push(),
            "SEQ__PUSH_VEL": seq_push_vel(),
            "INIT": init()
        }
        self.view_type = view_sel
        self.view = views[view_sel]

    def change_color(self, step, color) -> None:
        self.view[step] = color

def empty_view() -> list:
    view = []
    for _ in range(64):
        view.append("blank")
    return view

def init() -> list:
    view = []
    for _ in range(8*3):
        view.append("yellow")
    for i in range(8):
        if i==0 or i==7:
            view.append("red")
        elif i==3 or i==4:
            view.append("purple")
        else:
            view.append("blank")
    for i in range(8*4):
        if i%8 < 4:
            view.append("green_accent")
        else:
            view.append("light_blue")
    return view

def seq_and_drums() -> list:
    view = []
    for _ in range(8*4):
        view.append("blank")
    for i in range(4):
        for j in range(8):
            if j < 4:
                view.append("green")
            else:
                if i == 0:
                    if j == 4:
                        view.append("grey_accent")
                    else:
                        view.append("grey")
                else:
                    view.append("purple")
    return view

def seq_and_keyboard() -> list:
    view = []
    for _ in range(8*4):
        view.append("blank")
    for i in range(2):
        for i in range(2):
            for j in range(8):
                if i == 0:
                    if j == 0 or j == 3 or j == 7:
                        view.append("blank")
                    else:
                        view.append("yellow")
                else:
                    view.append("yellow")
    return view

def seq_and_push() -> list:
    view = []
    for _ in range(8*4):
        view.append("blank")
    for i in range(8):
        if i < 4:
            view.append("blank")
        elif i == 4:
            view.append("grey_accent")
        else:
            view.append("grey")
    #TODO Add four buttons for gate length per note
    for i in range(8*3):
        if i==1 or i==12 or i==16 or i==23:
            view.append("purple")
        else:
            view.append("light_blue")
    return view

def seq_push_vel() -> list:
    view = []
    for _ in range(8*4):
        view.append("blank")
    for i in range(8):
        if i < 4:
            view.append("purple")
    for i in range(8*3):
        if i==1 or i==12 or i==16 or i==23:
            view.append("purple")
        else:
            view.append("light_blue")
    return view
    

def seq_full() -> list:
    view = []
    for _ in range(64):
        view.append("blank")
    return view

def seq_four(top_left: int = 1, top_right: int = 2, bottom_left: int = 3, bottom_right: int = 4) -> list:
    view = []
    for i in range(64):
        mod = i % 8
        div = math.trunc(i / 8)
        if (mod <= 3 and div <= 3):
            view.append(top_left)
        elif (mod > 3 and div <= 3):
            view.append(top_right)
        elif (mod <= 3 and div > 3):
            view.append(bottom_left)
        elif (mod > 3 and div > 3):
            view.append(bottom_right)
    return view