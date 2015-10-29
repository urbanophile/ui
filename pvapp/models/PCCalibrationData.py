import numpy as np
from util.Constants import CHANNEL_INDEX


class PCCalibrationData(object):

    def __init__(self):
        self.calibration_mean = None
        self.calibration_std = None

    def update_data(self, data):
            self.pc_calibration_mean = np.mean(data[:, CHANNEL_INDEX['PC']])
            self.pc_calibration_std = np.std(data[:, CHANNEL_INDEX['PC']])

    def as_dict(self):
        return {
            "pc_calibration_mean": self.calibration_mean,
            "pc_calibration_std": self.calibration_std
        }
