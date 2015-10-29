import unittest
from mock import patch
from hardware.daq import LightPulse, WaveformThread
from models.ExperimentSettings import ExperimentSettings
import numpy as np


@patch("hardware.daq.ctypes")
class WaveformThreadTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.settings = ExperimentSettings()
        self.lp = LightPulse(self.settings)

    def test_init(self, mock_waveform_thread):
        WaveformThread(
            waveform=self.lp.create_waveform(),
            Channel='ao1',
            Time=np.float64(1.011),
            input_voltage_range=10.0,
            output_voltage_range=self.settings.output_voltage_range,
            input_sample_rate=self.settings.sample_rate,
            output_sample_rate=self.settings.output_sample_rate
        )
