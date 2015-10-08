import unittest
import numpy as np
from hardware.daq import LightPulse
from util.Models import ExperimentSettings


class LightPulseTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.lp = LightPulse(
            ExperimentSettings()
        )

    # def test_init_

    def test_can_create_pulse_array(self):

        pulse_array = self.lp.create_waveform()
        self.assertTrue(np.any(pulse_array))

        # make value
        self.assertTrue(np.any(np.amax(pulse_array) < 150.0))

        self.assertTrue(self.lp.A > 0)

        initial_offset = int(1.2)
        np.testing.assert_array_equal(
            np.zeros(initial_offset),
            pulse_array[:initial_offset]
        )

        final_offset = int(12.0)
        np.testing.assert_array_equal(
            np.zeros(final_offset),
            pulse_array[-final_offset:]
        )


        self.assertEqual(
            len(pulse_array[initial_offset:-final_offset]),
            1200
        )

    def test_scale_to_threshold(self):
        # setup tests
        self.lp.Voltage_Threshold = 0.08152173913043478
        voltage_waveform = 6 * np.ones(10)
        test_array = np.array([
            5.83695652174, 5.83695652174, 5.83695652174,
            5.83695652174, 5.83695652174, 5.83695652174,
            5.83695652174, 5.83695652174, 5.83695652174, 5.83695652174
        ])

        #
        scaled_array = self.lp.scale_to_threshold(voltage_waveform)

        # assertions
        np.testing.assert_almost_equal(
            scaled_array,
            test_array,
            decimal=11,
            verbose=True
        )

    def test_final_pulse_array_function(self):
        example_array = np.loadtxt(
            "test/data/sample_sin_waveformthread_write_data.csv"
        )
        self.lp.Waveform = "Sin"
        pulse_array = self.lp.create_waveform()
        np.savetxt('test_sine_array', pulse_array)
        np.testing.assert_almost_equal(
            pulse_array,
            example_array
        )

    def test_sin_function(self):
        pulse_array = self.lp.Sin(np.linspace(0, 1, 1200), 0.5)
        t = np.linspace(0, 1, 1200)
        amp = 0.5
        pi = np.pi
        np.testing.assert_array_equal(
            pulse_array,
            -(amp) * np.abs(np.sin(pi * t / t[-1]))
        )

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
