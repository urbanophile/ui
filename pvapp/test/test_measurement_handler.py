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

        mock_waveform_thread.__init__.return_value = True
        mock_waveform_thread.return_value.time = 3
        mock_waveform_thread.return_value.Read_Data = np.array([])
        # self.assertEqual(type(mock_waveform_thread), "MockClass")

        handler = MeasurementHandler(self.lp.create_waveform(), self.settings)
        handler.SingleMeasurement()

        mock_waveform_thread.__init__.assert_called_once_with(['ao1'])
        # self.assertTrue(mock_os.remove.called)
