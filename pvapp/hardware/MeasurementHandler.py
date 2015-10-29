import numpy as np
import logging
import time

from collections import deque

from hardware.daq import WaveformThread
from models.LightPulse import LightPulse
from util.utils import save_data


class MeasurementHandler(object):
    """
    Controller to handle IO from NI datacard
    """
    def __init__(self):

        self._queue = deque()

        self.NUM_CHANNELS = 3.

        self._logger = logging.getLogger()

    def _run_thread(self, daq_io_thread, metadata):
        """
        Sends a single version of waveform to the specified channel
        Returns:
        """

        daq_io_thread.setup()
        daq_io_thread.run()
        daq_io_thread.stop()

        print("Thread time: ", daq_io_thread.time)
        return daq_io_thread.Read_Data, daq_io_thread.time

    def add_to_queue(self, waveform_array, metadata):
        print("add_to_queue")
        daq_io_thread = WaveformThread(
            waveform=waveform_array,
            Channel=metadata.channel_name,
            Time=np.float64(metadata.get_total_time()),
            input_voltage_range=metadata.input_voltage_range,
            output_voltage_range=metadata.output_voltage_range,
            input_sample_rate=metadata.sample_rate,
            output_sample_rate=metadata.output_sample_rate
        )
        self._queue.append((daq_io_thread, metadata))

    def clear_queue(self, waveform_array, metadata):
        self._queue = deque()

    def single_measurement(self):
        thread_time = None
        data_set = []

        element = self._queue.popleft()

        averaging = element[1].averaging
        assert averaging > 0, "Averaging={0}".format(averaging)

        measurement_data, thread_time = self._run_thread(element[0], element[1])

        if averaging > 1:
            for i in range(averaging - 1):
                thread_data, thread_time = self._run_thread(element[0], element[1])
                measurement_data = np.vstack((thread_data,
                                              measurement_data))
                # RunningTotal is weighted by the number of points
                measurement_data = np.average(measurement_data,
                                              axis=0,
                                              weights=(1, i + 1))

        # what are going to be read

        data_set = np.empty((int(measurement_data.shape[0] / self.NUM_CHANNELS), self.NUM_CHANNELS))

        for i in range(int(self.NUM_CHANNELS)):
            # The data should be outputed one of each other, so divide it
            # up and roll it out
            row_length = data_set.shape[0]
            data_set[:, i] = measurement_data[i * row_length:(i + 1) * row_length]

        data_set = np.vstack((thread_time, data_set.T)).T
        return data_set

    def series_measurement(self, data_dir, wafer_name):
        dataset_list = []
        total_measurements = 0

        for element in self._queue:
            single_dataset = self.single_measurement()
            dataset_list.append(single_dataset)
            total_measurements = total_measurements + 1
            ts = int(time.time())
            dataset_name = str(total_measurements) + wafer_name + str(ts)
            save_data(single_dataset, dataset_name, data_dir)
            self._logger.info(
                'Measurement #{0} complete'.format(total_measurements)
            )
        self._logger.info(
            'Total: {0} measurements performed'.format(total_measurements)
        )

        return dataset_list

    def pc_calibration_measurement(self, calibration_settings):

        null_pulse = LightPulse(calibration_settings)

        self.add_to_queue(
            null_pulse.complete_waveform,
            calibration_settings
        )

        return self.single_measurement()

    def as_list(self):
        experiment_list = []
        for experiment in self._queue:
            experiment_list.append(experiment[1].as_dict())
        return experiment_list
