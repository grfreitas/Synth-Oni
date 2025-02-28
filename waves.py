import os

import numpy as np
import pandas as pd

from scipy.signal import sawtooth, square
from smoothing import smooth

from adsr import Envelope


_script_dir = os.path.dirname(__file__)
_file_path = os.path.join(os.path.dirname(__file__), 'utils', 'notesFrequencies')

FREQUENCY_DATA = pd.read_csv(_file_path)
FREQUENCY_MAP = dict(zip(FREQUENCY_DATA.note, FREQUENCY_DATA.frequency))


class Wave(np.ndarray):

    signal = None   

    def __new__(cls, frequency, duration, samplerate=44100):
        if isinstance(frequency, str):
            try:
                frequency = FREQUENCY_MAP[frequency]
            except KeyError:
                raise(f'Note should be one of {FREQUENCY_MAP.keys()}')

        ts = np.arange(0, duration, 1 / samplerate)
        cls._set_signal(2 * np.pi * frequency * ts)

        obj = np.asarray(cls.signal, dtype=np.float32).view(cls)
        obj.__setattr__('samplerate', samplerate)
        obj.__setattr__('duration', duration)

        return obj


class SawTooth(Wave):
    @classmethod
    def _set_signal(cls, x):
        cls.signal = sawtooth(x)


class Triangle(Wave):
    @classmethod
    def _set_signal(cls, x):
        cls.signal = 2 * np.abs(sawtooth(x)) - 1


class Square(Wave):
    @classmethod
    def _set_signal(cls, x):
        cls.signal = square(x)


class Sine(Wave):
    @classmethod
    def _set_signal(cls, x):
        cls.signal = np.sin(x)
