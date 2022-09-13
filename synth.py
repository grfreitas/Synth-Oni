import random

import numpy as np
import pandas as pd
import sounddevice as sd

from waves import SawTooth, Triangle, Square, Sine
from smoothing import smooth

FREQUENCY_DATA = pd.read_csv('utils/notesFrequencies')

FREQUENCY_MAP = dict(zip(FREQUENCY_DATA.note, FREQUENCY_DATA.frequency))

WAVEFORM_MAP = {
    'sawtooth': SawTooth,
    'triangle': Triangle,
    'square': Square,
    'sine': Sine
}


class Sequential(np.ndarray):
    
    def __new__(cls, signals=None, name=None, repeat=1):
        """Parallelizes sound signals.

        Args:
            signals: Optionals array of signals to parallelize.
            name: Optional name for the signal.

        Returns:
            np.array: Parallelized signals.
        """
        if signals is None:
            seq = np.array([])
        else:
            if not isinstance(signals, (list, tuple)):
                signals = [signals]
            seq = np.tile(np.concatenate(signals), repeat)

        obj = np.asarray(seq, dtype=np.float32).view(cls)
        obj.__setattr__('name', name)

        return obj

    def add(self, signal):
        return np.concatenate([self[:], signal])


class Arpeggio(np.ndarray):

    def __new__(cls, notes, waveform, mode, note_duration):
        """Create arpeggio of notes.

        Args:
            notes (list): Notes to arpeggiate over;
            waveform (string): Waveform of the arpeggio notes;
            mode (string): Arpeggio mode, can be up, down, updown or random;
            note_duration (float): Time in seconds of each note.

        Returns:
            np.array: Single instance of arppegio, should be sequentiated after creation.
        """

        if waveform.lower() not in ['sawtooth', 'triangle', 'square', 'sine']:
            raise KeyError("Wave should be one of: sawtooth, triangle, square, sine")

        if mode == 'up':
            arpeggio = [WAVEFORM_MAP[waveform](note, note_duration) for note in notes]
        elif mode == 'down':
            arpeggio = [WAVEFORM_MAP[waveform](note, note_duration) for note in notes[::-1]]
        elif mode == 'updown':
            arpeggio = [WAVEFORM_MAP[waveform](note, note_duration) for note in notes + notes[-2:0:-1]]
        else:
            raise KeyError("Mode should be one of: up, down, updown.")

        obj = np.asarray(np.concatenate(arpeggio), dtype=np.float32).view(cls)

        return obj


class Channel(dict):

    def __init__(self):
        pass


class Synth:
    
    def __init__(self):
        self.channels = Channel()

    def play(self, channel=0, loop=False, blocking=False):
        signal = self.channels[channel]
        sd.play(
            signal,
            samplerate=getattr(signal, 'samplerate', 44100),
            loop=loop,
            blocking=blocking
        )

    @staticmethod
    def halt(ignore_errors=True):
        sd.stop(ignore_errors)

    def set_channel(self, signal, channel, volume=1, smoothing=True):
        self.channels[channel] = volume * (smooth(signal) if smoothing else signal)
    
    def clear_channel(self, number):
        self.channels[channel] = None
