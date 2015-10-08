import unittest

from mock import PropertyMock, patch
import numpy as np
from hardware.daq import LightPulse
from hardware.MeasurementHandler import MeasurementHandler
from util.Models import ExperimentSettings



@patch("hardware.MeasurementHandler.WaveformThread", autospec=True)
class LightPulseTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.settings = ExperimentSettings()

        self.lp = LightPulse(self.settings)

    def test_SingleMeasurement(self, mock_waveform_thread):

        mock_waveform_thread.return_value.time = 3
        mock_waveform_thread.return_value.Read_Data = np.array([])

        handler = MeasurementHandler(self.lp.create_waveform(), self.settings)
        handler.SingleMeasurement()

