from copy import deepcopy

import numpy as np


class Envelope:

    def __init__(self, attackTime, decayTime, sustainLevel, releaseTime, samplerate) -> None:
        self.attackTime = attackTime
        self.decayTime = decayTime
        self.sustainLevel = sustainLevel
        self.releaseTime = releaseTime
        self._sr = samplerate

    def __call__(self, wave):
        return self._apply_envelope(wave)

    def _apply_envelope(self, wave):
        new_wave = self._apply_attack(wave)
        new_wave = self._apply_decay(new_wave)
        new_wave = self._apply_sustain(new_wave)
        new_wave = self._apply_release(new_wave)
        return new_wave

    def _apply_attack(self, wave):
        new_wave = deepcopy(wave)
        ls = np.linspace(-1, 0, round(self.attackTime * self._sr))
        new_wave[0: round(self.attackTime * self._sr)] *= 1 - (ls ** 2)
        return new_wave

    def _apply_decay(self, wave):
        new_wave = deepcopy(wave)
        ls = np.linspace(-1, 0, round(self.decayTime * self._sr))
        new_wave[
            round(self.attackTime * self._sr):
            round((self.attackTime + self.decayTime) * self._sr)
        ] *= ls ** 2 * (1 - self.sustainLevel) + self.sustainLevel
        return new_wave

    def _apply_sustain(self, wave):
        new_wave = deepcopy(wave)
        new_wave[
            round((self.attackTime + self.decayTime) * self._sr):
            len(wave) - self.releaseTime * self._sr
        ] *= self.sustainLevel
        return new_wave

    def _apply_release(self, wave):
        new_wave = deepcopy(wave)
        ls = np.linspace(-1, 0, round(self.releaseTime * self._sr))
        new_wave[
            round(len(wave) - self.releaseTime * self._sr):
        ] *= ls ** 4 * self.sustainLevel
        return new_wave
