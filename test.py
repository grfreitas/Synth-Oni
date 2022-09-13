import time

from waves import SawTooth
from synth import Sequential, Synth, Arpeggio


def main():

    arp1 = Arpeggio(
        notes=['C3', 'E3', 'G3', 'B3', 'C4'],
        waveform='sawtooth',
        mode='updown',
        note_duration=0.175
    )

    arp2 = Arpeggio(
        notes=['E2', 'E3', 'G3', 'B3', 'C4'],
        waveform='sawtooth',
        mode='updown',
        note_duration=0.175
    )

    seq = Sequential([
        Sequential(arp1, repeat=4),
        Sequential(arp2, repeat=4)
    ])

    synth = Synth()
    synth.set_channel(seq, 0)
    synth.play(channel=0, blocking=True, loop=True)



if __name__ == '__main__':
    main()
