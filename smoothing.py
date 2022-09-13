import numpy as np

SMOOTHING_OPTIONS = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']


def smooth(x, window_len=30, window='hanning'):
    
    if x.ndim != 1:
        raise ValueError('Smooth only accepts 1 dimension arrays.')
    elif x.size < window_len:
        raise ValueError('Input vector needs to be bigger than window size.')
    elif window_len < 3:
        return x
    elif not window in SMOOTHING_OPTIONS:
        raise ValueError(f"Window should be one of {SMOOTHING_OPTIONS}")
    elif window == 'flat':
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    s = np.r_[x[window_len-1: 0: -1], x, x[-2: -window_len-1: -1]]
    return np.convolve(w / w.sum(), s, mode='valid')
