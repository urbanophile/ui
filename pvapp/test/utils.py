import numpy as np
from scipy.signal import sawtooth


def sawtooth_waveform(num=500, var=0.2):
    t = np.linspace(0, 1, 500)
    return signal.sawtooth(2 * np.pi * 5 * t)


def make_sin_data(num=301, var=0.2, duration=1):
    t = np.linspace(0, duration, num)
    ref = np.sin(np.linspace(0, 2 * np.pi, num)) + var * np.random.rand(num)
    pc = np.zeros(num) + var * np.random.rand(num)
    pl = np.zeros(num) + var * np.random.rand(num)
    return np.column_stack((t, ref, pc, pl))


def make_sawtooth_data(num=501, var=0.2):
    t = np.linspace(0, 1, num)
    ref = sawtooth_waveform() + var * np.random.rand(num)
    pc = np.log(sawtooth_waveform() + var * np.random.rand(num))
    pl = np.log(np.log(sawtooth_waveform() + var * np.random.rand(num)))
    return np.column_stack((t, ref, pc, pl))
