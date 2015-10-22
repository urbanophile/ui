import unittest
import os
import sys
import numpy as np

# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from util.utils import save_data, save_metadata, load_metadata


class LoadSaveTest(unittest.TestCase):

                    # waveform=config['waveform'],
                    # duration=config['duration'],
                    # amplitude=config['amplitude'],
                    # offset_before=config['offset_before'],
                    # offset_after=config['offset_after'],
                    # sample_rate=config['sample_rate'],
                    # channel=config['channel'],
                    # binning=config['binning'],
                    # averaging=config['averaging']


    @classmethod
    def setUpClass(cls):
        cls.test_metadata = {
            "waveform": "sin",

            "Channel": "Low (50mA/V)",
            "Intensity_v": 4,
            "Measurement_Binning": 1,
            "Offset_Before_ms": 4.0,
            "Offset_After_ms": 5.0,
            "Peroid_s": 1.0,
            "Threshold_mA": 150.0,

            "Averaging": 1,
        }

        cls.multiple_settings = [
            {
                "Averaging": 1,
                "Channel": "Low (50mA/V)",
                "Intensity_v": 4,
                "Measurement_Binning": 1,
                "Offset_After_ms": 5.0,
                "Offset_Before_ms": 4.0,
                "Peroid_s": 1.0,
                "Threshold_mA": 150.0,
                "Waveform": "FrequencyScan"
            },
            {
                "Averaging": 1,
                "Channel": "Low (50mA/V)",
                "Intensity_v": 4,
                "Measurement_Binning": 1,
                "Offset_After_ms": 5.0,
                "Offset_Before_ms": 4.0,
                "Peroid_s": 1.0,
                "Threshold_mA": 150.0,
                "Waveform": "FrequencyScan"
            },
            {
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
        ]

        cls.test_data = np.array([1, 1, 1, 1])
        cls.fname = "test_data"
        cls.fpath = os.path.join(os.getcwd(), 'test', 'data')
        cls.check_dat_path = os.path.join(cls.fpath, cls.fname + '.tsv')
        cls.check_inf_path = os.path.join(cls.fpath, cls.fname + '.json')

    def test_write_data_to_file(self):
        save_data(
            LoadSaveTest.test_data,
            LoadSaveTest.fname,
            LoadSaveTest.fpath
        )
        self.assertTrue(os.path.isfile(LoadSaveTest.check_dat_path))

    def test_write_metadata_to_same_path(self):
        save_metadata(
            LoadSaveTest.test_metadata,
            LoadSaveTest.fname,
            LoadSaveTest.fpath
        )
        self.assertTrue(os.path.isfile(LoadSaveTest.check_inf_path))

    def test_load_inf_file(self):
        """Check return an metadata dictionary with same keys"""
        load_path = os.path.join(LoadSaveTest.fpath, 'test_data.json')
        metadata = load_metadata(load_path)
        loaded_items = set(LoadSaveTest.test_metadata.items())
        reference_items = set(metadata.items())
        self.assertEqual(len(loaded_items & reference_items), 9)

    # @classmethod
    # def tearDownClass(cls):
    #     os.remove(cls.check_dat_path)
    #     os.remove(cls.check_inf_path)
