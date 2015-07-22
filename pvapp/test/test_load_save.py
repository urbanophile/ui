import unittest
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from pvapp.main import OutputData, LightPulse


class LoadSaveTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_metadata = {
            "Averaging": 1,
            "Channel": "Low (50mA/V)",
            "Intensity_v": 4,
            "Measurement_Binning": 1,
            "Offset_After_ms": 5.0,
            "Offset_Before_ms": 4.0,
            "Peroid_s": 1.0,
            "Threshold_mA": 150.0,
            "Waveform": "FrequencyScan"
        }
        cls.test_data = np.array([1, 1, 1, 1])
        cls.fname = "test_data"
        cls.fpath = os.path.join(os.getcwd(), 'test', 'data')
        cls.check_dat_path = os.path.join(cls.fpath, cls.fname + '.dat')
        cls.check_inf_path = os.path.join(cls.fpath, cls.fname + '.inf')

    def test_write_data_to_file(self):
        OutputData().save_data(
            LoadSaveTest.test_data,
            LoadSaveTest.fname,
            LoadSaveTest.fpath
        )
        self.assertTrue(os.path.isfile(LoadSaveTest.check_dat_path))

    def test_write_metadata_to_same_path(self):
        OutputData().save_metadata(
            LoadSaveTest.test_metadata,
            LoadSaveTest.fname,
            LoadSaveTest.fpath
        )
        self.assertTrue(os.path.isfile(LoadSaveTest.check_inf_path))

    def test_load_inf_file(self):
        """Check return an metadata dictionary with same keys"""
        load_path = os.path.join(LoadSaveTest.fpath, 'raw_test_data.inf')
        metadata = OutputData().load_metadata(load_path)
        loaded_items = set(LoadSaveTest.test_metadata.items())
        reference_items = set(metadata.items())
        self.assertEqual(len(loaded_items & reference_items), 9)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.check_dat_path)
        os.remove(cls.check_inf_path)


class LightPulseTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.lp = LightPulse(
            'Cos',
            amplitude=-0.5,
            offset_before=0.0,
            offset_after=0.0,
            duration=5,
            voltage_threshold=0.081527139,
            sample_frequency=1
        )

    def test_can_create_lightpulse_object(self):

        pulse_array = self.lp.create_waveform()
        self.assertTrue(np.any(pulse_array))

    # def test_bad_initialisation_lightpulse_values_fail(self):
    #     pass

    # def test_sin_function(self):
    #     pass

    def test_square_function(self):
        pulse_array = self.lp.Square(np.linspace(0, 5, 5), -6)
        self.assertTrue(np.all(pulse_array == (6 * np.ones(5))))

    # def test_cos_function(self):
    #     pass

    def test_triangle_function(self):
        pulse_array = self.lp.Triangle(np.arange(5), -4)
        self.assertTrue(np.all(pulse_array == np.array([0, 2, 4, 2, 0])))

if __name__ == '__main__':
    unittest.main()
