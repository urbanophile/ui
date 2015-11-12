from models.TemperatureSettings import TemperatureSettings
from util.models import PVInputError
import unittest


class TemperatureSettingsTest(unittest.TestCase):

    # def test_init_
    def test_can_valid_temperature_settings(self, ):
        temp_settings = TemperatureSettings(
            start_temp=20,
            end_temp=30,
            step_temp=5
        )
        self.assertTrue(isinstance(temp_settings, TemperatureSettings))

    def test_too_big_step_size(self):
        self.assertRaises(PVInputError, TemperatureSettings, 20, 30, 30)

    def test_uneven_step_size(self):
        self.assertRaises(PVInputError, TemperatureSettings, 20, 30, 7.5)

    def test_too_many_steps(self):
        self.assertRaises(PVInputError, TemperatureSettings, 20, 20, 15)
