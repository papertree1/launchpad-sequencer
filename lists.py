leds = [#91, 92, 93, 94, 95, 96, 97, 98, 99,
        81, 82, 83, 84, 85, 86, 87, 88, #89,
        71, 72, 73, 74, 75, 76, 77, 78, #79,
        61, 62, 63, 64, 65, 66, 67, 68, #69,
        51, 52, 53, 54, 55, 56, 57, 58, #59,
        41, 42, 43, 44, 45, 46, 47, 48, #49,
        31, 32, 33, 34, 35, 36, 37, 38, #39,
        21, 22, 23, 24, 25, 26, 27, 28, #29,
        11, 12, 13, 14, 15, 16, 17, 18] #19

colors = {
    0: 0,
    1: 62,
    2: 44,
    3: 57,
    4: 89,
    5: 78,
    6: 99,
    7: 12,
    8: 23,
    9: 32,
    10: 49,
    11: 53,
    12: 65,
    13: 70,
    14: 80,
    15: 90,
    16: 82,
    #...
    "blank": 0,
    "black": 1,
    "grey": 2,
    "grey_accent": 3,
    "red": 72,
    "light_blue": 29,
    "blue": 37,
    "green": 21,
    "green_accent": 16,
    "yellow": 97,
    "purple": 43,
    "purple_accent": 44
}

'''
Setting MIDI notes to easily indexable drum voices, following General MIDI
https://musescore.org/sites/musescore.org/files/General%20MIDI%20Standard%20Percussion%20Set%20Key%20Map.pdf
'''
drumNotes = [
    36, # C1 Bass Drum 1 
    37, # C#1 Side Stick 
    38, # D1 Acoustic Snare 
    39, # Eb1 Hand Clap 
    40, # E1 Electric Snare 
    41, # F1 Low Floor Tom 
    42, # F#1 Closed Hi Hat 
    43, # G1 High Floor Tom 
    44, # Ab1 Pedal Hi-Hat 
    45, # A1 Low Tom 
    46, # Bb1 Open Hi-Hat 
    47, # B1 Low-Mid Tom 
    48, # C2 Hi Mid Tom 
    49, # C#2 Crash Cymbal 1 
    50, # D2 High Tom 
    51, # Eb2 Ride Cymbal 1
]
velocities = {
    15: 7,
    16: 17,
    17: 27,
    18: 37,
    25: 47,
    26: 57,
    27: 67,
    28: 77,
    35: 87,
    36: 97,
    37: 107,
    38: 127
}

drums = {
    41: 1,
    42: 2,
    43: 3,
    44: 4,
    31: 5,
    32: 6,
    33: 7,
    34: 8,
    21: 9,
    22: 10,
    23: 11,
    24: 12,
    11: 13,
    12: 14,
    13: 15,
    14: 16
}

melodic = {
    45: 1,
    46: 2,
    47: 3,
    48: 4,
    35: 5,
    36: 6,
    37: 7,
    38: 8,
    25: 9,
    26: 10,
    27: 11,
    28: 12,
    15: 13,
    16: 14,
    17: 15,
    18: 16
}

seq_and_push_keys = {
    11: 60, #Middle C
    12: 62, #61
    13: 64, #62
    14: 65, #63
    15: 67, #64
    16: 69, #65
    17: 71, #66
    18: 72, #67
    21: 65,
    22: 67,
    23: 69,
    24: 71,
    25: 72,
    26: 74,
    27: 76,
    28: 77,
    31: 71,
    32: 72,
    33: 74,
    34: 76,
    35: 77,
    36: 79,
    37: 81,
    38: 83,
}