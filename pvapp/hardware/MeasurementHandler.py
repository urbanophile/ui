import numpy as np
from hardware.daq import WaveformThread


class MeasurementHandler():
    """
    Controller to handle IO from NI datacard

    Attributes
    ----------
    """
    def __init__(self, waveform, metadata):

        self.LightPulse = waveform
        self.Time = np.float64(metadata.get_total_time())
        self.Averaging = int(metadata.averaging)
        self.Channel = metadata.channel_name

        self.output_voltage_range = metadata.OutputVoltageRange
        self.input_voltage_range = metadata.InputVoltageRange

        self.SampleRate = metadata.sample_rate

    def SingleMeasurement(self):
        """
        Sends a single version of waveform to the specified channel
        Returns:
        """
        print("MeasurementHandler: SingleMeasure")
        # start playing waveform
        mythread = WaveformThread(
            waveform=self.LightPulse,
            Channel=self.Channel,
            Time=self.Time,
            input_voltage_range=self.input_voltage_range,
            output_voltage_range=self.output_voltage_range,
            input_sample_rate=self.SampleRate,
            output_sample_rate=1.2e3
        )
        mythread.run()
        mythread.stop()

        print("Thread time: ", mythread.time)
        return mythread.Read_Data, mythread.time

    def Measure(self):
        print("MeasurementHandler: Measure")
        NUM_CHANNELS = 3.
        thread_time = None

        assert self.Averaging > 0, "Averaging ={0}".format(self.Averaging)

        measurement_data, thread_time = self.SingleMeasurement()

        if self.Averaging > 1:
            for i in range(self.Averaging - 1):
                print("Thread time: ", thread_time)
                self.SingleMeasurement()
                thread_data, thread_time = self.SingleMeasurement()
                measurement_data = np.vstack((thread_data,
                                              measurement_data))
                # RunningTotal is weighted by the number of points
                measurement_data = np.average(measurement_data,
                                              axis=0,
                                              weights=(1, i + 1))

        # what are going to be read
        print "Data value: ", measurement_data,
        print "data type: ", type(measurement_data)
        data_set = np.empty((int(measurement_data.shape[0] / NUM_CHANNELS), NUM_CHANNELS))

        for i in range(int(NUM_CHANNELS)):
            # The data should be outputed one of each other, so divide it
            # up and roll it out
            row_length = data_set.shape[0]
            data_set[:, i] = measurement_data[i * row_length:(i + 1) * row_length]

        return np.vstack((thread_time, data_set.T)).T
