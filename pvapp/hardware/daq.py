import ctypes
import threading
import numpy as np

from util.Constants import (
    MAX_OUTPUT_SAMPLE_RATE,
    MAX_INPUT_SAMPLE_RATE,
    CHANNELS
)

try:
    nidaq = ctypes.windll.nicaiu  # load the DLL
except AttributeError as e:
    print "DLL not found {0}".format(e)
except e:
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


# ### nidaq.DAQmxCreateTask
# creates a task, which must be later cleared
# returns a taskHandle obje

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


class WaveformThread(threading.Thread):
    """
    This class performs the necessary initialization of the DAQ hardware and
    spawns a thread to handle playback of the signal.
    It takes as input arguments the waveform to play and the sample rate at
    which to play it.
    This will play an arbitrary-length waveform file.

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

        print("Channel: ", Channel)
        assert isinstance(waveform, np.ndarray)
        assert Channel in ['ao1', 'ao0']
        assert input_voltage_range in [10, 5, 2, 1]
        assert isinstance(Time, np.float64)
        assert output_sample_rate <= MAX_OUTPUT_SAMPLE_RATE
        assert input_sample_rate <= MAX_INPUT_SAMPLE_RATE

        self.DEVICE_ID = "Dev3/"

        self.running = True

        self.periodLength = int((Time * output_sample_rate).item())

        self.sampleRate = float64(output_sample_rate)  # output sample rate
        self.input_sample_rate = float64(input_sample_rate)

        #
        self.Time = Time

        # Analogue output channel on which the waveform will be played
        self.Channel = Channel

        # this controls the input voltage range. (+-10,+-5, +-2,+-1)
        self.InputVoltageRange = input_voltage_range
        self.OutputVoltageRange = output_voltage_range

        # These are IDs for the the read and write tasks
        self.taskHandle_Write = TaskHandle(0)
        self.taskHandle_Read = TaskHandle(1)

        self.Write_data = np.zeros((self.periodLength,), dtype=np.float64)

        # BUG: this doesn't copy the waveform exactly
        # several trailing numbers are truncated.
        assert self.periodLength
        print("Len periodLength: ", self.periodLength)
        print("len waveform.shape: ", waveform.shape)
        for i in range(self.periodLength - 1):
            self.Write_data[i] = waveform[i]
        # self.Write_data = np.copy(waveform)

        # Note: this ensures that the DAQ the LED is not on after the last
        # part of the waveform has been played.
        self.Write_data[int(self.periodLength) - 1] = 0

        # functions to configure the DAQ through the API
        # TODO: configure this so app doesn't crash when
        # self.setup()

    def setup(self):
        self.Setup_Write()
        self.Setup_Read(self.Time, self.input_sample_rate)

    def Setup_Write(self):
        print('Waveform: Setup_Write')

        # convert waveform to a numpy array

        # setup the DAQ hardware
        print('DAQmxCreateTask')
        self.CHK(nidaq.DAQmxCreateTask(
            "",
            ctypes.byref(self.taskHandle_Write)
        ))

        print('DAQmxCreateAOVoltageChan')
        self.CHK(nidaq.DAQmxCreateAOVoltageChan(
            self.taskHandle_Write,
            self.DEVICE_ID + self.Channel,
            "",
            float64(-self.OutputVoltageRange),
            float64(self.OutputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))
        print("OutputVoltageRange: ", self.OutputVoltageRange)
        print(np.max(self.Write_data))

        print("Sample rate :", self.sampleRate)
        print('DAQmxCfgSampClkTiming')
        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Write,
            "/" + self.DEVICE_ID + "ai/SampleClock",
            self.sampleRate,   # samples per channel
            self.DAQmx_Val_Rising,   # active edge
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.periodLength)
        ))

        print('DAQmxWriteAnalogF64')
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
        print('Finish Setup_Write')

    def Setup_Read(self, Time, input_sample_rate):
        print('Waveform: Setup_Read')

        self.max_num_samples = int(np.float32(input_sample_rate) * 3 * Time)
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandle_Read)))

        print('DAQmxCreateAIVoltageChan')
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

        print('DAQmxCfgSampClkTiming')
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

        self.Read_Data = np.zeros((self.max_num_samples,), dtype=np.float64)
        self.read = int32()

    def CHK(self, err):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError(
                'nidaq call failed with error %d: %s' % (err, repr(buf.value))
            )
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise RuntimeError(
                'nidaq generated warning %d: %s' % (err, repr(buf.value))
            )

    def run(self):
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Write))
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Read))

        self.CHK(nidaq.DAQmxReadAnalogF64(
            # Task handle
            self.taskHandle_Read,
            # numSamples per channel, -1 reads as many samples as possible
            -1,
            # Timeout in seconds
            float64(10.0),
            self.DAQmx_Val_GroupByScanNumber,
            # read array
            self.Read_Data.ctypes.data,
            # samples per channel
            self.max_num_samples,
            # The actual number of samples read per channel (its an output)
            ctypes.byref(self.read),
            None
        ))  # reserved for future use, pass none to this
        # toc = time.clock()
        # print self.Time
        self.time = np.linspace(0, self.Time, self.read.value)
        # print self.time[0]

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
