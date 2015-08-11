import ctypes
import json
import threading
import numpy as np
from numpy import pi
from scipy import signal
from ConfigParser import SafeConfigParser

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


config = SafeConfigParser()
config.read('nidaq.ini')


# max is float64(1e6), well its 1.25MS/s/channel
DAQmx_InputSampleRate = float64(1.2e6)
DAQmx_OutPutSampleRate = float64(1.2e6)  # Its 3.33MS/s

# Constants associated with NI-DAQmx
DAQmx_Val_Cfg_Default = int32(-1)
DAQmax_Channels_Number = 3


# ### nidaq.DAQmxCreateTask
# creates a task, which must be later cleared
# returns a taskHandle object

# ### nidaq.DAQmxCreateAIVoltageChan
# creates an analog input voltage channel

# ### nidaq.DAQmxCreateAOVoltageChan
# Creates channel(s) to generate voltage and adds the channel(s) to
# the task you specify with taskHandle.

# ### nidaq.DAQmxStartTask
# Transitions the task from the committed state to the running state,
# which begins measurement or generation.

# ### nidaq.DAQmxStopTask
# Stops the task and returns it to the state it was in before you
# called DAQmxStartTask

# ### nidaq.DAQmxClearTask
# clears the specified task. If the task is currently running, the
# function first stops thetask and then releases all of its resources.

# ### nidaq.DAQmxReadAnalogF64
# reads samples from the specified acquisition task.

# ### nidaq.DAQmxWriteAnalogF64
# The NI-DAQmx Write Function moves samples from the
# Application Development Environment (ADE) Memory to the PC Buffer in RAM.

# ### nidaq.DAQmxGetErrorString
# Converts the error number returned
# by an NI-DAQmx function into a meaningful error message.

# ### nidaq.DAQmxCfgSampClkTiming
# Your device uses a sample clock to control the rate at which samples
# are acquired and generated. This sample clock sets the time interval
#  between samples. Each tick of this clock initiates the acquisition
# or generation of one sample per channel.
# This function sets the source of the sample clock, the rate of the
# sample clock, and the number of samples to acquire or generate




class DAQWrapper(object):
    """docstring for DAQWrapper"""
    def __init__(self, arg):
        super(DAQWrapper, self).__init__()
        self.arg = arg
        try:
            self.daq = ctypes.windll.nicaiu  # load the DLL
        except:
            pass

    def stop_task():
        pass


class WaveformThread(threading.Thread):
    """
    This class performs the necessary initialization of the DAQ hardware and
    spawns a thread to handle playback of the signal.
    It takes as input arguments the waveform to play and the sample rate at
    which to play it.
    This will play an arbitrary-length waveform file.

    Attributes
    ----------

    running
    sampleRate
    periodLength
    time

    """

    DAQmx_Val_Volts = 10348
    DAQmx_Val_Rising = 10280
    DAQmx_Val_FiniteSamps = 10178
    DAQmx_Val_ContSamps = 10123
    DAQmx_Val_GroupByChannel = 0

    DAQmx_Val_Diff = int32(-1)

    # AllowedInputVoltage = json.loads(config.get("NI-DAQ", "InputVoltageRange"))
    # InputVoltageRange = 10

    # this controls the  output voltage range. Minimum is -5 to 5
    OutputVoltageRange = 5

    # this places the points one at a time from each channel, I think
    DAQmx_Val_GroupByScanNumber = 0

    def __init__(self, waveform, Channel, Time, input_voltage_range=10):

        self.running = True
        self.sampleRate = DAQmx_OutPutSampleRate
        self.periodLength = Time * DAQmx_OutPutSampleRate
        self.Time = Time
        self.Channel = Channel

        # this controls the input voltage range. (+-10,+-5, +-2,+-1)
        assert input_voltage_range in [10, 5, 2, 1]
        self.InputVoltageRange = input_voltage_range

        self.taskHandle_Write = TaskHandle(0)
        self.taskHandle_Read = TaskHandle(1)

        self.Write_data = np.zeros((self.periodLength,), dtype=np.float64)

        for i in range(self.periodLength):
            self.Write_data[i] = waveform[i]

        # functions to configure the DAQ
        self.Setup_Write()
        self.Setup_Read(Time)

    def Setup_Write(self):
        # convert waveform to a numpy array

        # setup the DAQ hardware
        self.CHK(nidaq.DAQmxCreateTask(
            "",
            ctypes.byref(self.taskHandle_Write)
        ))

        self.CHK(nidaq.DAQmxCreateAOVoltageChan(
            self.taskHandle_Write,
            "Dev3/" + self.Channel,
            "",
            float64(-self.OutputVoltageRange),
            float64(self.OutputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))

        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Write,
            "/Dev3/ai/SampleClock",
            self.sampleRate,   # samples per channel
            self.DAQmx_Val_Rising,   # active edge
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.periodLength)
        ))

        self.CHK(nidaq.DAQmxWriteAnalogF64(
            self.taskHandle_Write,  # TaskHandel
            int32(self.periodLength),  # num of samples per channel
            0,  # autostart, if not done, a NI-DAQmx Start function is required
            float64(-1),  # Timeout
            self.DAQmx_Val_GroupByChannel,  # Data layout
            self.Write_data.ctypes.data,  # write array
            None,  # samplers per channel written
            None
        ))  # reserved
        threading.Thread.__init__(self)

    def Setup_Read(self, Time):

        self.max_num_samples = int(np.float32(DAQmx_InputSampleRate) * 3 * Time)
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandle_Read)))

        self.CHK(nidaq.DAQmxCreateAIVoltageChan(
            self.taskHandle_Read,
            "Dev3/ai0:2",
            "",
            self.DAQmx_Val_Diff,  # this is the rise type
            float64(-self.InputVoltageRange),
            float64(self.InputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))

        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Read,
            "",
            # "/Dev3/ao/SampleClock",
            # "ao/SampleClock",
            # "Dev3/"+self.Channel+"/SampleClock"- doesn't work,
            DAQmx_InputSampleRate,
            self.DAQmx_Val_Rising,
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.max_num_samples)
        ))

        self.Read_Data = np.zeros((self.max_num_samples,), dtype=np.float64)
        self.read = int32()

    def CHK(self, err):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s' % (err, repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError('nidaq generated warning %d: %s' % (err, repr(buf.value)))

    def run(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Write))
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Read))

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
        # toc = time.clock()
        # print self.Time
        self.time = np.linspace(0, self.Time, self.read.value)
        # print self.time[0]

        # This check was performed to determine if the set frequency was
        # actually what was measured. It appears it is.
        # print self.read.value
        # print (toc - tic)*1e6
        # print 'Minimum time reading',(toc - tic)*1e6/(self.read.value)
        # plot(self.Read_Data)
        # show()
        # print self.read
        return self.Read_Data

    def stop(self):
        self.running = False
        if self.taskHandle_Write.value != 0:
            nidaq.DAQmxStopTask(self.taskHandle_Write)
            nidaq.DAQmxClearTask(self.taskHandle_Write)

        if self.taskHandle_Read.value != 0:
            nidaq.DAQmxStopTask(self.taskHandle_Read)
            nidaq.DAQmxClearTask(self.taskHandle_Read)
        # show()

    def clear(self):
        nidaq.DAQmxClearTask(self.taskHandle_Write)
        nidaq.DAQmxClearTask(self.taskHandle_Read)


class MeasurementHandler():
    """
    Controller to handle IO from NI datacard

    Attributes
    ----------
    """
    def __init__(self, OutPutVoltage, Averaging, Channel, Time, InputVoltageRange):
        self.OutPutVoltage = OutPutVoltage
        self.SampleRate = DAQmx_OutPutSampleRate
        self.Time = Time
        self.Averaging = int(Averaging)
        self.Channel = Channel
        self.AllowedInputVoltage = json.loads(config.get("NI-DAQ", "InputVoltageRange"))
        self.InputVoltageRange

    def SingleMeasurement(self):
        """
        Sends a single version of waveform to the specified channel
        Returns:
        """

        # start playing waveform
        mythread = WaveformThread(
            self.OutPutVoltage,
            self.Channel,
            self.Time,
            self.input_voltage_range
        )
        mythread.run()
        mythread.stop()

        self.time = mythread.time
        return mythread.Read_Data

    def Average(self):
        # If there is an error, put this line inside SingleMeasurement

        RunningTotal = self.SingleMeasurement()

        for i in range(self.Averaging - 1):
            RunningTotal = np.vstack((self.SingleMeasurement(), RunningTotal))
            # The running total is weighted for the number of points inside it
            RunningTotal = np.average(RunningTotal, axis=0, weights=(1, i + 1))
        return RunningTotal

    def Measure(self):
        NUM_CHANNELS = 3.

        assert self.Averaging > 0, "Averaging ={0}".format(self.Averaging)

        data = self.Average()
        # Here the 3 stands for the number of channels
        # what are going to be read
        Data = np.empty((int(data.shape[0] / NUM_CHANNELS), NUM_CHANNELS))
        # print Data.shape,data.shape
        for i in range(int(NUM_CHANNELS)):
            # The data should be outputted one of each other, so divide it
            # up and roll it out
            Data[:, i] = data[i * Data.shape[0]:(i + 1) * Data.shape[0]]

        return np.vstack((self.time, Data.T)).T


class LightPulse():
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

    def __init__(self, waveform, amplitude, offset_before, offset_after,
                 duration, voltage_threshold,
                 sample_frequency=np.float32(DAQmx_OutPutSampleRate)):

        assert duration > 0
        assert offset_after >= 0
        assert offset_before >= 0
        assert amplitude > 0

        self.Waveform = waveform
        self.A = - amplitude
        self.Offset_Before = offset_before
        self.Offset_After = offset_after
        self.Duration = duration
        self.output_samples = sample_frequency
        self.Voltage_Threshold = voltage_threshold
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
            result = getattr(self, self.Waveform)(self.Duration)
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
        Returns t sized array with values -A
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
