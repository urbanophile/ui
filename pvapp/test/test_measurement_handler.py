import unittest

from mock import patch
import numpy as np

from hardware.daq import LightPulse
from hardware.MeasurementHandler import MeasurementHandler
from util.Models import ExperimentSettings

from testfixtures import log_capture


@patch("hardware.MeasurementHandler.WaveformThread", autospec=True)
class MeasurementHandlerTest(unittest.TestCase):
    # np.set_printoptions(threshold='nan')
    def setUp(self):
        self.settings = ExperimentSettings()

        self.lp = LightPulse(self.settings)

    def test__run_thread(self, mock_waveform_thread):

        mock_waveform_thread.return_value.time = 3
        mock_waveform_thread.return_value.Read_Data = np.array([])

        handler = MeasurementHandler()
        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        # handler._run_thread()

    def test_single_measurement_no_averaging(self, mock_waveform_thread):

        handler = MeasurementHandler()
        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        return_tuple = (np.array([1, 2, 3, 4, 5, 6]), np.array([0, 1]))

        with patch.object(handler, '_run_thread',
                          return_value=return_tuple) as method:
            test_dataset = handler.single_measurement()
            self.assertEqual(1, method.call_count)
            np.testing.assert_array_equal(
                test_dataset,
                np.array([[0, 1, 3, 5], [1, 2, 4, 6]])
            )

        self.assertEqual(len(handler._queue), 0)

    def test_single_measurement_with_averaging(self, mock_waveform_thread):
        # setup
        settings = ExperimentSettings()
        settings.averaging = 2
        handler = MeasurementHandler()
        return_tuple = [
            (np.array([2, 3, 4, 5, 6, 7]), np.array([0, 1])),
            (np.array([3, 4, 5, 6, 7, 8]), np.array([0, 1])),
        ]

        handler.add_to_queue(self.lp.create_waveform(), settings)

        with patch.object(handler, '_run_thread', side_effect=return_tuple) as method:
            # perform
            test_dataset = handler.single_measurement()

            # assert
            self.assertEqual(2, method.call_count)
            np.testing.assert_array_equal(
                test_dataset,
                np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]])
            )

        self.assertEqual(len(handler._queue), 0)


    def test_add_to_queue(self, mock_waveform_thread):
        handler = MeasurementHandler()
        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        self.assertEqual(len(handler._queue), 1)

    @log_capture()
    def test_series_measurement_empty_queue(self, mock_waveform_thread,
                                            log_checker):

        handler = MeasurementHandler()

        observed_data_list = handler.series_measurement()
        self.assertEqual(
            len(observed_data_list), 0)

        log_checker.check(
            ('root', 'INFO', 'Total: 0 measurements performed'),
        )

    @log_capture()
    def test_series_measurement_one_in_queue(self, mock_waveform_thread,
                                             log_checker):

        # setup
        handler = MeasurementHandler()
        print(handler._queue)

        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        side_effect_array = [
            np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]])
        ]

        with patch.object(handler, 'single_measurement',
                          side_effect=side_effect_array) as method:
            # perform
            observed_data_list = handler.series_measurement()

        # assert
        for observed_data in observed_data_list:
            np.testing.assert_array_equal(
                observed_data,
                np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]])
            )

        log_checker.check(
            ('root', 'INFO', 'Measurement #1 complete'),
            ('root', 'INFO', 'Total: 1 measurements performed'),
        )

    @log_capture()
    def test_series_measurement_multiple_queue(self, mock_waveform_thread,
                                               log_checker):

        side_effect_array = [
            np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]]),
            np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]]),
            np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]])
        ]

        handler = MeasurementHandler()

        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        handler.add_to_queue(self.lp.create_waveform(), self.settings)
        handler.add_to_queue(self.lp.create_waveform(), self.settings)

        with patch.object(handler, 'single_measurement',
                          side_effect=side_effect_array) as method:
            observed_data_list = handler.series_measurement()

        for observed_data in observed_data_list:
            np.testing.assert_array_equal(
                observed_data,
                np.array([[0, 2.5, 4.5, 6.5], [1, 3.5, 5.5, 7.5]])
            )
        log_checker.check(
            ('root', 'INFO', 'Measurement #1 complete'),
            ('root', 'INFO', 'Measurement #2 complete'),
            ('root', 'INFO', 'Measurement #3 complete'),
            ('root', 'INFO', 'Total: 3 measurements performed'),
        )
