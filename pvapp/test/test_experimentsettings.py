import unittest
import numpy as np
from util.Models import ExperimentSettings


class ExperimentSettingsTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.meta_data = ExperimentSettings()
        self.maxDiff = None

    def test_get_settings_as_dict(self):
        meta_data = {
            'channel': 'High (2A/V)',
            'averaging': 1,
            'measurement_binning': 1,
            'threshold_mA': 150,
            "inverted_channels": {
                'Reference': False,
                'PC': False,
                'PL': True
            },

            'sample_rate': 1.2e3,
            'output_sample_rate': 1.2e3,

            "InputVoltageRange": 10.0,
            "OutputVoltageRange": 10.0,
            "waveform": 'Sin',
            "amplitude": 0.5,

            "offset_before": 1,
            "offset_after": 10,
            "duration": 1,
            "voltage_threshold": 0.08152173913043478,
            "channel_name": 'ao0',

            #
            "pc_calibration_mean": None,
            "pc_calibration_std": None
        }
        self.assertDictEqual(self.meta_data.get_settings_as_dict(), meta_data)

    def test_init(self):
        self.assertEqual(
            self.meta_data.voltage_threshold,
            0.08152173913043478,
        )
        self.assertEqual(
            self.meta_data.channel_name,
            'ao0'
        )

    def test_set_amplitude(self):
        self.assertTrue(self.meta_data.amplitude, 0.5)

    def test_set_amplitude_too_high(self):
        self.meta_data.channel = 'Low (50mA/V)'
        self.meta_data.amplitude = 15
        self.assertEqual(self.meta_data.amplitude, 10)

        self.meta_data.channel = 'High (2A/V)'
        self.meta_data.amplitude = 15
        self.assertEqual(self.meta_data.amplitude, 1.5)

    def test_set_voltage_too_high(self):
        pass

    def test_set_sample_rate_too_high(self):
        self.meta_data.sample_rate = 9e90
        self.assertEqual(self.meta_data.sample_rate, 1.2e6)


