import numpy as np


def make_sin_data(num=301, var=0.2):
    t = np.linspace(0, 1, num)
    ref = np.sin(np.linspace(0, 2 * np.pi, num)) + var * np.random.rand(num)
    pc = np.zeros(num) + var * np.random.rand(num)
    pl = np.zeros(num) + var * np.random.rand(num)
    return np.column_stack((t, ref, pc, pl))
