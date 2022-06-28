import numpy as np

from scipy.signal import sawtooth, square


class Wave(np.ndarray):

    signal = None

    def __new__(cls, frequency, duration, sampling_rate=44100):

        ts = np.arange(0, duration, duration / sampling_rate)
        domain = 2 * np.pi * frequency * ts
        cls._set_signal(domain)

        obj = np.asarray(cls.signal, dtype=np.float32).view(cls)
        obj.__setattr__('sampling_rate', sampling_rate)

        return obj

    def _set_signal(self):
        pass


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
