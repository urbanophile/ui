import unittest
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from pvapp.main import OutputData


class LoadSaveTest(unittest.TestCase):

    def setup(self):
        pass

    def test_write_data_to_file(self):
        test_data = np.array([1, 1, 1, 1])
        fname = "test_data"
        fpath = os.getcwd()

        OutputData().save_data(test_data, fname, fpath)
        self.assertTrue(os.path.isfile(fname + '.dat'))

    def test_write_data_to_path(self):
        pass

    def test_write_data_to_windoz(self):
        pass

    def test_write_metadata_to_same_path(self):
        test_data = np.array([1, 1, 1, 1])
        fname = "test_data"
        fpath = os.getcwd()
        OutputData().save_data(test_data, fname, fpath)
        self.assertTrue(os.path.isfile(fname + '.inf'))

    def test_load_inf_file(self):
        """Checks this return an appropriate waveform object"""
        pass


class LightPulseTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
