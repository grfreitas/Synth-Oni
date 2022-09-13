import numpy as np


class Envelope:

    def __init__(self, attack, decay, sustain, release, duration) -> None:
        self._attack = attack
        self._decay = decay
        self._sustain = sustain
        self._release = release
        self._duration = duration

    def __call__(self, wave):
        return self._apply_envelope(wave)

    def _apply_envelope(self, wave):
        self.sr = getattr(wave, 'samplerate', 44100)

        wave = self._apply_attack(wave)
        wave = self._apply_decay(wave)
        wave = self._apply_sustain(wave)
        wave = self._apply_release(wave)

        return wave

    def _apply_attack(self, wave):
        ls = np.linspace(-1, 0, round(self._attack * self.sr))
        wave[0: round(self._attack * self.sr)] *= 1 - (ls ** 2)
        return wave

    def _apply_decay(self, wave):
        ls = np.linspace(-1, 0, round(self._decay * self.sr))
        wave[
            round(self._attack * self.sr):
            round((self._attack + self._decay) * self.sr)
        ] *= ls ** 2 * (1 - self._sustain) + self._sustain
        return wave

    def _apply_sustain(self, wave):
        wave[
            round((self._attack * self._decay) * self.sr): 
            round((self._duration - self._release) * self.sr)
        ] *= self._sustain
        return wave

    def _apply_release(self, wave):
        ls = np.linspace(-1, 0, round(self._release * self.sr))
        wave[
            round((self._duration - self._release) * self.sr):
            round(self._duration * self.sr)
        ] *= ls ** 4 * self._sustain
        return wave
