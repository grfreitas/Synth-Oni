import os

import random
from adsr import Envelope

import numpy as np
import pandas as pd
import sounddevice as sd

from waves import SawTooth, Triangle, Square, Sine
from smoothing import smooth

_script_dir = os.path.dirname(__file__)
_file_path = os.path.join(os.path.dirname(__file__), 'utils', 'notesFrequencies')

FREQUENCY_DATA = pd.read_csv(_file_path)
FREQUENCY_MAP = dict(zip(FREQUENCY_DATA.note, FREQUENCY_DATA.frequency))

WAVEFORM_MAP = {
    'sawtooth': SawTooth,
    'triangle': Triangle,
    'square': Square,
    'sine': Sine
}


class Sequential(np.ndarray):
    
    def __new__(cls, signals=None, name=None, repeat=1, samplerate=44100):
        """Sequentiate sound signals.

        Args:
            signals: Optionals array of waves to sequentiate.
            name: Optional name for the signal.

        Returns:
            np.array: Sequentiate signals.
        """
        if signals is None:
            seq = np.array([])
        else:
            if not isinstance(signals, (list, tuple)):
                signals = [signals]

            concat = [np.pad(
                signals[i],
                pad_width=(np.size(signals[0:i]),
                           np.size(signals[i+1:])),
                mode='constant') for i in range(len(signals))]

            seq = np.tile(np.add.reduce(concat), repeat)

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


class WaveCreator:

    def __init__(self, envelope) -> None:
        self.envelope = envelope

    def triangle(self, frequency, key_duration):
        total_duration = key_duration + self.envelope.releaseTime        
        return self.envelope(Triangle(frequency, total_duration))

    def sine(self, frequency, key_duration):
        total_duration = key_duration + self.envelope.releaseTime        
        return self.envelope(Sine(frequency, total_duration))

    def square(self, frequency, key_duration):
        total_duration = key_duration + self.envelope.releaseTime        
        return self.envelope(Square(frequency, total_duration))

    def sawtooth(self, frequency, key_duration):
        total_duration = key_duration + self.envelope.releaseTime       
        wave = SawTooth(frequency, total_duration) 
        return self.envelope(wave)


class Channel:

    def __init__(self, n, samplerate=44100):

        self.n = n
        self.samplerate = samplerate
        self.set_envelope()

    def set_envelope(self, attackTime=0.2, decayTime=0.2, sustainLevel=0.5, releaseTime=0.2):

        self.envelope = Envelope(
            attackTime=attackTime,
            decayTime=decayTime,
            sustainLevel=sustainLevel,
            releaseTime=releaseTime,
            samplerate=self.samplerate
        )

        self.wave = WaveCreator(self.envelope)

class Synth:
    
    def __init__(self, total_channels=4):
        self.channels = {k: Channel(n=k) for k in range(total_channels)}

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
