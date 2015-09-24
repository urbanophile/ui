import ctypes
import threading
import numpy as np
from numpy import pi
from scipy import signal
from util.Constants import (
    MAX_OUTPUT_SAMPLE_RATE,
    MAX_INPUT_SAMPLE_RATE,
    CHANNELS
)

try:
    nidaq = ctypes.windll.nicaiu  # load the DLL
except Exception, e:
    print(e)

##############################
# Setup some typedefs and constants
# to correspond with values in NI-DAQ driver files located
# NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double

# alias for reasons (???)
TaskHandle = uInt32

# converted to ctype floats for use with the DLL
# DAQmx_OutPutSampleRate = float64(MAX_OUTPUT_SAMPLE_RATE)
DAQmx_InputSampleRate = float64(MAX_INPUT_SAMPLE_RATE)


# Constants associated with NI-DAQmx
DAQmx_Val_Cfg_Default = int32(-1)
DAQmax_Channels_Number = len(CHANNELS)


class WaveformThread(threading.Thread):
    """
    This class performs the necessary initialization of the DAQ hardware and
    spawns a thread to handle playback of the signal. It will play an
    arbitrary-length waveform file.
    """

    DAQmx_Val_Volts = 10348
    DAQmx_Val_Rising = 10280
    DAQmx_Val_FiniteSamps = 10178
    DAQmx_Val_ContSamps = 10123
    DAQmx_Val_GroupByChannel = 0

    DAQmx_Val_Diff = int32(-1)

    # this places the points one at a time from each channel, I think
    DAQmx_Val_GroupByScanNumber = 0

    def __init__(self, waveform, Channel, Time,
                 input_voltage_range,
                 output_voltage_range,
                 output_sample_rate,
                 input_sample_rate):
        """
        :param waveform: a numpy array representating a waveform
        :param Channel: a string specifying the analog out channels
        :param Time: a numpy 64-bit float
        :param input_voltage_range: a positive integer representing the DAQ voltage input range
        :param output_voltage_range: a positive integer representing the
        :param output_sample_rate: the DAQ sample rate in samples per second
        :param input_sample_rate: the ADQ sample rate in samples per second
        :return: None
        """

        assert isinstance(waveform, np.ndarray)
        assert Channel in ['ao1', 'ao0']
        assert input_voltage_range in [10, 5, 2, 1]
        assert isinstance(Time, np.float64)
        assert output_sample_rate <= MAX_OUTPUT_SAMPLE_RATE
        assert input_sample_rate <= MAX_INPUT_SAMPLE_RATE

        self.DEVICE_ID = "Dev3/"

        self.running = True
        # output sample rate
        self.periodLength = int((Time * output_sample_rate).item())

        self.Write_data = np.zeros((self.periodLength,), dtype=np.float64)

        self.sampleRate = float64(1.2e3) # float64(output_sample_rate) # output sample rate
        self.input_sample_rate = float64(input_sample_rate)

        self.max_num_samples = int(np.float32(input_sample_rate) * 3 * Time)

        self.Read_Data = np.zeros((self.max_num_samples,), dtype=np.float64)
        self.read = int32()

        self.Time = Time
        self.Channel = Channel

        # this controls the input voltage range. (+-10,+-5, +-2,+-1)
        self.InputVoltageRange = input_voltage_range
        self.OutputVoltageRange = output_voltage_range

        self.taskHandle_Write = TaskHandle(0)
        self.taskHandle_Read = TaskHandle(1)


        assert self.periodLength
        for i in range(self.periodLength):
            self.Write_data[i] = waveform[i]

        # functions to configure the DAQ
        self._setup_write()
        self._setup_read(self.Time, self.input_sample_rate)

    def _setup_write(self):
        """
        Method to setup the DAQ to write out the selected waveform
        :return: None
        """
        print('Waveform: _setup_write')

        # setup the DAQ hardware
        print('DAQmxCreateTask')
        self.CHK(nidaq.DAQmxCreateTask(
            "",
            ctypes.byref(self.taskHandle_Write)
        ))

        # Creates channel(s) to generate voltage and adds the channel(s) to
        # the task you specify with taskHandle.
        self.CHK(nidaq.DAQmxCreateAOVoltageChan(
            self.taskHandle_Write,
            self.DEVICE_ID + self.Channel,
            "",
            float64(-self.OutputVoltageRange),
            float64(self.OutputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))

        # Configures the sample clock which controls the rate at
        # which samples are acquired and generated.
        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Write,
            "/" + self.DEVICE_ID + "ai/SampleClock",
            self.sampleRate,   # samples per channel
            self.DAQmx_Val_Rising,   # active edge
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.periodLength)
        ))

        # Moves samples from  Application Development Environment (ADE) Memory
        # to the PC Buffer in RAM.
        self.CHK(nidaq.DAQmxWriteAnalogF64(
            self.taskHandle_Write,  # TaskHandel
            int32(self.periodLength),  # num of samples per channel
            0,  # autostart, if not done, a NI-DAQmx Start function is required
            float64(-1),  # Timeout
            self.DAQmx_Val_GroupByChannel,  # Data layout
            self.Write_data.ctypes.data,  # write array
            None,  # samplers per channel written
            None
        ))
        threading.Thread.__init__(self)

    def _setup_read(self, Time, input_sample_rate):
        """
        Sets up the DAQ to read analog input after playing the waveform.

        :param Time: a numpy 64 bit float64
        :param input_sample_rate: a
        :return: None
        """

        # creates a task which must be later cleared
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandle_Read)))

        # creates an analog input voltage channel
        self.CHK(nidaq.DAQmxCreateAIVoltageChan(
            self.taskHandle_Read,
            self.DEVICE_ID + "ai0:2",
            "",
            self.DAQmx_Val_Diff,  # this is the rise type
            float64(-self.InputVoltageRange),
            float64(self.InputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))

        # Configures the sample clock which controls the rate at
        # which samples are acquired and generated.
        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Read,
            "",
            # "/Dev3/ao/SampleClock",
            # "ao/SampleClock",
            # "Dev3/"+self.Channel+"/SampleClock"- doesn't work,
            input_sample_rate,
            self.DAQmx_Val_Rising,
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.max_num_samples)
        ))

    def CHK(self, err):
        """
        An error checking function to interpret the DAQ errors

        :param err: an integer representing a NI DAQ dll error code
        :return: None
        :raises RuntimeError: a python error with description of dll error
        """


        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)

            # retrieves the associated DAQ error string
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s' % (err, repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)

            # retrieves the associated DAQ error string
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq generated warning %d: %s' % (err, repr(buf.value)))

    def run(self):
        """
        Starts currently setup tasks

        :return: a numpy array of the data read from the DAQ
        """
        # creates tasks for reading and writing from the DAQ
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Write))
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Read))

        # reads samples from the specified acquisition task.
        self.CHK(nidaq.DAQmxReadAnalogF64(
            self.taskHandle_Read,  # Task handle
            -1,  # numSamples per channel, -1 reads as many samples as possible
            float64(10.0),    # Timeout in seconds
            self.DAQmx_Val_GroupByScanNumber,
            # DAQmx_Val_GroupByChannel,
            # DAQmx_Val_GroupByScanNumber,
            self.Read_Data.ctypes.data,  # read array
            self.max_num_samples,   # samples per channel
            ctypes.byref(self.read),  # The actual number of samples read per channel (its an output)
            None
        ))  # reserved for future use, pass none to this

        # create an array of time values corresponding to each sample
        self.time = np.linspace(0, self.Time, self.read.value)

        return self.Read_Data

    def stop(self):
        """
        Stops and clears any currently running tasks from the workspace
        :return: None
        """

        self.running = False
        if self.taskHandle_Write.value != 0:
            nidaq.DAQmxStopTask(self.taskHandle_Write)
            nidaq.DAQmxClearTask(self.taskHandle_Write)

        if self.taskHandle_Read.value != 0:
            nidaq.DAQmxStopTask(self.taskHandle_Read)
            nidaq.DAQmxClearTask(self.taskHandle_Read)

    def clear(self):
        """
        Removes the DAQ task from workspace
        :return: None
        """
        nidaq.DAQmxClearTask(self.taskHandle_Write)
        nidaq.DAQmxClearTask(self.taskHandle_Read)


class MeasurementHandler(object):
    """
    Controller to handle IO from NI datacard
    """
    def __init__(self, waveform, metadata):
        """

        :param waveform: a numpy array of floats which represent a specified waveform
        :param metadata: a object contain the parameters needed for the DAQ
        :return: None
        """

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

        :returns mythread.Read_Data: an numpy array of measurement values
        :returns mythread.time: a numpy array of the corresponding measurement times
        """
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

        return mythread.Read_Data, mythread.time

    def Measure(self):
        """
        Performs multiple measurements including averaging the results if necessary

        :returns np.vstack((thread_time, data_set.T)).T: an numpy array of times
        and measurement values
        """

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
        data_set = np.empty((int(measurement_data.shape[0] / NUM_CHANNELS), NUM_CHANNELS))

        for i in range(int(NUM_CHANNELS)):
            # The data should be outputted on top of each other, so divide it
            # up and roll it out
            row_length = data_set.shape[0]
            data_set[:, i] = measurement_data[i * row_length:(i + 1) * row_length]

        return np.vstack((thread_time, data_set.T)).T


class LightPulse(object):
    """
    Represents different wave forms to be sent to play

    Attributes
    ----------
    Waveform: str
        String for waveform type in Sin, FrequencyScan, Square, Cos,
        Triangle, MJ
    Amplitude: float
        negative and in volts
    Offset_Before: float
        in milliseconds
    Offset_After: float
        in milliseconds
    Duration: float
        a positive time in milliseconds
    Voltage_Threshold: float
        ???
    time_array: array
        evenly spaced points over the time interval
    complete_waveform: array
        array of waveform intensity values including offsets
    """

    def __init__(self, metadata):

        assert metadata.duration > 0
        assert metadata.offset_after >= 0
        assert metadata.offset_before >= 0
        assert metadata.amplitude > 0
        assert metadata.sample_rate > 0

        self.Waveform = metadata.waveform
        self.A = - metadata.amplitude
        self.Offset_Before = metadata.offset_before
        self.Offset_After = metadata.offset_after
        self.Duration = metadata.duration
        self.output_samples = np.float32(metadata.sample_rate)
        self.Voltage_Threshold = metadata.voltage_threshold
        self.time_array = np.array([])

        self.complete_waveform = self.create_waveform()

        self._set_derived_parameters()

    def __repr__(self):
        description = (
            "<LightPulse object: {0}, {1} A, {2} Time, {3} V Threshold>"
        ).format(
            self.Waveform,
            self.A,
            self.Duration,
            self.Voltage_Threshold
        )
        return description

    def _set_derived_parameters(self):
        self.total_time = self.Duration + self.Offset_Before / 1000 + self.Offset_After / 1000
        self.frequence_val = 1. / self.total_time

    # TODO: should be private method
    def create_waveform(self):
        """
        Factory method to produce numpy array with light intensity values
        :returns:
        """
        # pad waveform with zeroes
        v_before = np.zeros(
            int(self.output_samples * self.Offset_Before / 1000)
        )
        v_after = np.zeros(
            int(self.output_samples * self.Offset_After / 1000)
        )

        if self.Waveform == 'FrequencyScan':
            # TODO: this is bad refactor
            result = self.FrequencyScan(self.Duration)
            voltage_waveform, self.time_array = result[0], result[1]
            voltage_waveform -= self.Voltage_Threshold

        else:
            self.time_array = np.linspace(
                0, self.Duration, num=self.output_samples * self.Duration
            )
            # TODO: this is bad, refactor
            voltage_waveform = getattr(self, self.Waveform)(
                self.time_array, self.A
            )
            voltage_waveform = self.scale_to_threshold(voltage_waveform)

        self.Duration = self.time_array[-1]
        complete_waveform = np.concatenate(
            (v_before, voltage_waveform, v_after)
        )

        total_time = sum([self.Offset_Before / 1000,
                          self.Offset_After / 1000,
                          self.Duration])
        self.time_array = np.linspace(
            0, total_time, num=complete_waveform.shape[0]
        )
        return complete_waveform

    # TODO: also should be Private method
    def scale_to_threshold(self, voltage_waveform):
        """
        Scales an array of voltage values to below voltage_threshold
        """
        #  everything is reversed because amplitude is negative
        max_voltage = np.amax(abs(voltage_waveform))
        if np.abs(max_voltage) > 0:
            scale_factor = (max_voltage - self.Voltage_Threshold) / max_voltage
            voltage_waveform *= scale_factor * voltage_waveform
        voltage_waveform -= self.Voltage_Threshold
        return voltage_waveform

    def Sin(self, time_array, amplitude):
        """
        Returns t sized array with values of sine wave over half the period
        """
        return -(amplitude) * np.abs(np.sin(pi * time_array / time_array[-1]))

    def Square(self, time_array, amplitude):
        """
        Returns t sized array with values -A
        """
        return -amplitude * np.ones((time_array.shape[0]))

    def Cos(self, time_array, amplitude):
        """
        Returns t sized array with equally spaced values sampled from
        0.5 * (cos(t) + A) over period 0 to pi
        """
        scale_factor = amplitude * 0.5
        cos_values = np.cos(pi * time_array / time_array[-1])
        return - scale_factor * cos_values - scale_factor

    # BUG: something is funny with the implementation doesn't
    def Triangle(self, time_array, amplitude, width=0.5):
        """
        Returns t sized array of equally spaced points from triangle wave
        with peak at t/2. See details in underlying scipy.signal.sawtooth
        """
        t_length = time_array.shape[0]
        wave = signal.sawtooth(2 * np.pi * np.linspace(0, 1, t_length), 0.5)
        return -amplitude * 0.5 * (wave + 1)

    def NullWave(self, time_array, amplitude):
        """
        :return: t sized array with values -A
        """
        return np.zeros((time_array.shape[0]))

    # TODO: rename to more  descriptive
    def MattiasCustom(self, time_array, amplitude):
        """
        Return t sized array evenly space points on 1/x on log scale
        """
        fraction = 0.01
        t_shift = time_array.shape[0] * fraction
        t0_index = time_array.shape[0] * (0.5 - fraction)
        midpoint = time_array.shape[0] / 2
        t_halfway = time_array[midpoint]

        # Functions are:
        # G = C/t
        # G = Bx^4 + Amplitude
        # These are then spliced together at t0

        B = -self.A * time_array[t_shift] ** (-4) / 5.
        C = 4. / 5 * self.A * time_array[t_shift]
        f = np.concatenate((
            -C / (time_array[:t0_index] - t_halfway),
            B * (time_array[t0_index:midpoint] - t_halfway) ** 4 + amplitude
        ))
        return -1 * np.concatenate((f, f[::-1]))

    def FrequencyScan(self, number):
        """
        Another custom Mattias function
        """
        Amplitudefreaction = 0.025
        Inital_Time_Delay = 0.01

        V = np.zeros(self.output_samples * .1)
        T = np.linspace(0, Inital_Time_Delay, self.output_samples * .1)
        t0 = T[-1]

        for f in np.logspace(self.Offset_Before, self.Offset_After, int(number))[::-1]:

            t = np.arange(0, 10 / f, 1. / self.output_samples)

            V = np.append(V, Amplitudefreaction * self.A * np.sin(2 * np.pi * f * t))

            T = np.append(T, t + t0)
            t0 += t[-1]

        return -V - self.A, T

    def get_settings_as_dict(self):
        pulse_parameters = {
            "Intensity_v": self.A,
            "Waveform": self.Waveform,
            "Period_s": self.Duration,
            "Offset_Before_ms": self.Offset_Before,
            "Offset_After_ms": self.Offset_After
        }
        return pulse_parameters

    def get_total_duration(self):
        return self.Duration + self.Offset_Before + self.Offset_After

    def last_t(self):
        return self.time_array[-1]
