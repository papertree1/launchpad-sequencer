from lists import leds, colors
import functions
import mido
import time as t
import math

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
            "SEQ_FOUR": seq_four() #TODO Opció per a canviar les veus individualment
        }
        self.view_type = view_sel
        self.view = views[view_sel]

    def change_color(self, step, color) -> None:
        self.view[step] = color

def empty_view() -> list:
    view = []
    for i in range(64):
        view.append("blank")
    return view

def seq_and_drums() -> list:
    view = []
    for i in range(8*4):
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
                    if i == 1 and j == 4:
                        view.append("purple_accent")
                    else:
                        view.append("purple")
    return view

def seq_and_keyboard() -> list:
    view = []
    for i in range(8*4):
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

def seq_full() -> list:
    view = []
    for i in range(64):
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