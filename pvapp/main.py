# -*- coding: utf-8 -*-

"""
This is a GUI for the QSSPL system. It interfaces with USB6356 NI DAQ card.
Currently it is assumed that the NI card is Dev3, and it reads three channels
and outputs on 1. This could all be changed, but i'm not sure why I want to
yet.

    To use this the NI drives need to be installed!

Things to improve:

    Definition of Dev/ and channels
    Selectable inputs and output voltage ranges.
    Make that you ca't load incorrect values (int and floats at least)
"""

import ctypes
import Gui_Main_v2 as gui  # import the newly created GUI file
import json
import matplotlib.pylab as plt
import numpy as np
import os  # importing wx files
import threading
import wx
import ConstantsClass
from CanvasClass import CanvasPanel
from math import pi


from scipy import signal

# load any DLLs
try:
    nidaq = ctypes.windll.nicaiu  # load the DLL
except:
    pass
##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# the constants

# max is float64(1e6), well its 1.25MS/s/channel
DAQmx_InputSampleRate = float64(1.2e6)
DAQmx_OutPutSampleRate = float64(1.2e6)  # Its 3.33MS/s


class WaveformThread(threading.Thread):
    """
    This class performs the necessary initialization of the DAQ hardware and
    spawns a thread to handle playback of the signal.
    It takes as input arguments the waveform to play and the sample rate at
    which to play it.
    This will play an arbitrary-length waveform file.
    """

    DAQmx_Val_Cfg_Default = int32(-1)
    DAQmx_Val_Volts = 10348
    DAQmx_Val_Rising = 10280
    DAQmx_Val_FiniteSamps = 10178
    DAQmx_Val_ContSamps = 10123
    DAQmx_Val_GroupByChannel = 0
    DAQmax_Channels_Number = 3

    DAQmx_Val_Diff = int32(-1)
    InputVoltageRange = 10  # this controls the input voltage range. (=-10,=-5, =-2,+-1)
    OutputVoltageRange = 5  # this controls the  output voltage range. Minimum is -5 to 5
    DAQmx_Val_GroupByScanNumber = 0  # this places the points one at a time from each channel, I think

    def __init__(self, waveform, Channel, Time):
        self.running = True
        self.sampleRate = DAQmx_OutPutSampleRate
        # self.periodLength = len( waveform )
        self.periodLength = Time * DAQmx_OutPutSampleRate
        self.Time = Time

        self.Write_data = np.zeros((self.periodLength,), dtype=np.float64)

        for i in range(self.periodLength):

            self.Write_data[i] = waveform[i]

        # plot(self.Write_data)
        # show()
        self.taskHandle_Write = TaskHandle(0)
        self.taskHandle_Read = TaskHandle(1)
        self.Channel = Channel
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
        # print Time
        self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref(self.taskHandle_Read)))

        self.CHK(nidaq.DAQmxCreateAIVoltageChan(
            self.taskHandle_Read,
            "Dev3/ai0:2",
            "",
            self.DAQmx_Val_Diff,  # DAQmx_Val_Diff,   #DAQmx_Val_RSE,       #DAQmx_Val_Cfg_Default, #this is the rise type
            float64(-self.InputVoltageRange),
            float64(self.InputVoltageRange),
            self.DAQmx_Val_Volts,
            None
        ))

        self.CHK(nidaq.DAQmxCfgSampClkTiming(
            self.taskHandle_Read,
            "",
            #"/Dev3/ao/SampleClock",
            #"ao/SampleClock",
            #"Dev3/"+self.Channel+"/SampleClock"-doesn;t work,
            DAQmx_InputSampleRate,
            self.DAQmx_Val_Rising,
            self.DAQmx_Val_FiniteSamps,
            uInt64(self.max_num_samples)
        ))
        #  DAQmxCfgSampClkTiming(taskHandle,"",sampleRate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sampsPerChan);
        #  DAQmx Start Code
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
        counter = 0
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Write))
        self.CHK(nidaq.DAQmxStartTask(self.taskHandle_Read))

        # DAQmx Read Code
        # tic = time.clock()

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
        assert amplitude < 0

        self.Waveform = waveform
        self.A = amplitude
        self.Offset_Before = offset_before
        self.Offset_After = offset_after
        self.Duration = duration
        self.output_samples = sample_frequency
        self.Voltage_Threshold = voltage_threshold
        self.time_array = np.array([])

        self.complete_waveform = self.create_waveform()

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

    # TODO: rename to more  descriptive
    def MJ(self, time_array, amplitude):
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
        Custom Mattias function
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


class TakeMeasurements():
    """
    Controller to handle IO from NI datacard
    """
    def __init__(self, OutPutVoltage, Averaging, Channel, Time):
        self.OutPutVoltage = OutPutVoltage
        self.SampleRate = DAQmx_OutPutSampleRate
        self.Time = Time
        # print self.Time,Time
        self.Averaging = int(Averaging)
        self.Channel = Channel


    def SingleMeasurement(self):

        # start playing waveform
        mythread = WaveformThread(self.OutPutVoltage, self.Channel, self.Time)
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
        NoChannls = 3.
        if self.Averaging > 0:

            data = self.Average()
            # Here the 3 stands for the number of channels what are going to be read
            Data = np.empty((int(data.shape[0] / NoChannls), NoChannls))
            # print Data.shape,data.shape
            for i in range(int(NoChannls)):
                # The data should be outputted one of each other, so divide it up and roll it out
                Data[:, i] = data[i * Data.shape[0]:(i + 1) * Data.shape[0]]

            return vstack((self.time, Data.T)).T
        else:
            print('Averaging Too low')


class OutputData():
    """
    This class handles loading and saving file data
    """

    Path = os.getcwd()
    LoadPath = os.getcwd()

    def save_data(self, data, filename, filepath):
        """
        Writes experimental data to TSV file
        """

        variables = 'Time (s)\tGeneration (V)\tPC (V)\tPL (V)'
        full_path = os.path.join(filepath, filename + '.dat')
        np.savetxt(full_path, data, delimiter='\t', header=variables)

    def save_metadata(self, metadata_dict, filename, filepath):
        """
        Writes experimental metadata to JSON file
        """
        print(metadata_dict, type(metadata_dict))
        assert type(metadata_dict) is dict

        full_path = os.path.join(filepath, filename + '.inf')
        serialised_json = json.dumps(
            metadata_dict,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )

        with open(full_path, 'w') as text_file:
                text_file.write(serialised_json)

    def load_metadata(self, full_filepath):
        """
        Loads metadata file and returns a python dictionary
        """

        with open(full_filepath, 'r') as f:
            file_contents = f.read()
            metadata_dict = json.loads(file_contents)

        return metadata_dict


class GUIController(gui.MyFrame1, OutputData):
    """
    Controller to handle interface with wx UI
    """
    # constructor
    measurement_type = 'Standard'

    def __init__(self, parent):
        # initialize parent class
        gui.MyFrame1.__init__(self, parent)

        self.Fig1 = CanvasPanel(self.Figure1_Panel)
        self.Fig1.labels('Raw Data', 'Time (s)', 'Voltage (V)')
        self.Data = np.array([])
        # CanvasPanel(self.Figure2_Panel)

    def Determine_Digital_Output_Channel(self):
        # Just a simple function choosing the correct output channel
        # based on the drop down box
        if self.Channel == 'High (2A/V)':
            Channel = r'ao0'
            # 1840 comes from exp measurements
            Voltage_Threshold = self.Threshold / 1840.
        elif self.Channel == r'Low (50mA/V)':
            Channel = r'ao1'
            # 66 comes from experimental measurements
            Voltage_Threshold = self.Threshold / 66.
            # Voltage_Threshold = 0 #apparently this is an equiptment thing
        print(self.Channel, self.Channel == r'Low (50mA/V)')

        return Channel, Voltage_Threshold

    def Save(self, event):
        """
        Method to handle dialogue window and saving data to file
        """
        # temp call to GetVAlues
        getattr(self, 'GetValues_' + self.measurement_type)(event)

        dialog = wx.FileDialog(
            None,
            'Save measurement data and metadata',
            self.Path,
            '',
            r'DAT and INF files (*.dat;*.inf)|*.inf;*.dat',
            wx.FD_SAVE
        )

        if dialog.ShowModal() == wx.ID_OK:
            dialog_path = dialog.GetPath()
            self.Path = os.path.dirname(dialog_path)
            self.SaveName = os.path.splitext(os.path.basename(dialog_path))[0]

            metadata_list = self.Make_List_For_Inf_Save(event)
            print(type(metadata_list), metadata_list.__class__.__name__)
            self.save_data(self.Data, self.SaveName, self.Path)
            self.save_metadata(metadata_list, self.SaveName, self.Path)

        else:
            print('Canceled save')
        dialog.Destroy()

        event.Skip()


    def Load(self, event):
        """
        Method to handle load metadata dialog window and update metadata state
        """

        dialog = wx.FileDialog(
            None,
            'Select a metadata file',
            self.LoadPath,
            '',
            r'*.inf',
            wx.FD_OPEN
        )

        if dialog.ShowModal() == wx.ID_OK:

            metadata_dict = self.load_metadata(dialog.GetPath())
            metadata_stringified = dict(
                [a, str(x)] for a, x in metadata_dict.iteritems()
            )
            print(metadata_stringified)
            # print(type(self.m_Intensity))
            self.m_Intensity.SetValue(metadata_stringified[u'Intensity_v'])
            self.m_Threshold.SetValue(metadata_stringified[u'Threshold_mA'])
            self.m_Waveform.SetStringSelection(metadata_stringified[u'Waveform'])
            self.m_Output.SetStringSelection(metadata_stringified[u'Channel'])
            self.m_Averaging.SetValue(metadata_stringified[u'Averaging'])
            try:
                self.m_Binning.SetValue(metadata_stringified[u'Measurement_Binning'])
            except:
                self.m_Binning.SetValue(metadata_stringified[u'Binning'])

            self.m_Offset_Before.SetValue(metadata_stringified[u'Offset_Before_ms'])
            self.m_Period.SetValue(metadata_stringified[u'Peroid_s'])
            self.m_Offset_After.SetValue(metadata_stringified[u'Offset_After_ms'])

        dialog.Destroy()
        event.Skip()

    def GetValues_Standard(self, event):

        # TODO: refactor so DRY this looks very non
        self.Intensity = self.CHK_float(self.m_Intensity, event)
        self.Binning = self.CHK_int(self.m_Binning, event)
        self.Averaging = self.CHK_int(self.m_Averaging, event)
        self.Peroid = self.CHK_float(self.m_Period, event)
        self.Offset_Before = self.CHK_float(self.m_Offset_Before, event)
        self.Offset_After = self.CHK_float(self.m_Offset_After, event)
        self.Waveform = self.m_Waveform.GetStringSelection()
        self.Channel = self.m_Output.GetStringSelection()
        self.Threshold = self.CHK_float(self.m_Threshold, event)
        # print self.Binning
        # print self.lo

    def Make_List_For_Inf_Save(self, event):

        Intensity_v = self.CHK_float(self.m_Intensity, event)
        Threshold_mA = self.CHK_float(self.m_Threshold, event)
        Waveform = self.m_Waveform.GetStringSelection()
        Channel = self.m_Output.GetStringSelection()
        Averaging = self.CHK_int(self.m_Averaging, event)
        Measurement_Binning = self.CHK_int(self.m_Binning, event)
        Offset_Before_ms = self.CHK_float(self.m_Offset_Before, event)
        Peroid_s = self.CHK_float(self.m_Period, event)
        Offset_After_ms = self.CHK_float(self.m_Offset_After, event)
        # REFACTOR: this has weird side effects
        metadata_dict = locals()
        del metadata_dict['self']
        del metadata_dict['event']
        return metadata_dict

    def Perform_Standard_Measurement(self, event):
        self.measurement_type = 'Standard'
        self.Perform_Measurement(event)
        self.PlotData()

    def Perform_Measurement(self, event):

        # this is what happens when the go button is pressed

        # first thing is all the inputs are grabbed
        # A check is performed, and if failed, event is skipped

        # print event.GetEventType()
        # print event.IsCommandEvent()
        # print event.GetId()

        getattr(self, 'GetValues_' + self.measurement_type)(event)

        # find what channel we are using, and what the voltage offset then is
        Channel, Voltage_Threshold = self.Determine_Digital_Output_Channel()

        self.CHK_Voltage_Threshold(Voltage_Threshold, event)

        # This the event hasn't been skipped then continue with the code.
        self.m_scrolledWindow1.Refresh()
        if not event.GetSkipped():

            #  Then the light pulse is defined, but the lightpulse class
            light_pulse = LightPulse(
                self.Waveform,
                self.Intensity,
                self.Offset_Before,
                self.Offset_After,
                self.Peroid,
                Voltage_Threshold
            )

            print(light_pulse.__repr__())
            #  We determine what channel to output on

            # We put all that info into the take measurement section, which is
            # a instance definition. There are also global variables that
            # go into this
            Go = TakeMeasurements(
                light_pulse.complete_waveform,
                self.Averaging,
                Channel,
                light_pulse.t[-1]
            )

            # print 'here'
            # Using that instance we then run the lights, and measure the outputs
            self.Data = self.Bin_Data(Go.Measure(), self.Binning)
            # self.Data = lightPulse.Define()
            # We then plot the datas, this has to be changed if the plots want to be updated on the fly.

            event.Skip()
        else:

            self.m_scrolledWindow1.Refresh()




    def PlotData(self, e=None):

        self.Fig1.clear()
        labels = ['Reference', 'PC', 'PL']
        # t = np.linspace(0,t[-1],self.Data.shape[0])
        colours = ['b', 'r', 'g']

        # this is done not to clog up the plot with many points
        if self.Data.shape[0] > 1000:
            num = self.Data.shape[0] // 1000
        else:
            num = 1

        if self.ChkBox_PL.GetValue():
            self.Data[:, 3] *= -1
        if self.ChkBox_PC.GetValue():
            self.Data[:, 2] *= -1
        if self.ChkBox_Ref.GetValue():
            self.Data[:, 1] *= -1

        # This plots the figure
        # print self.Data
        # print self.Data.shape,t.shape
        for i, label, colour in zip(self.Data[:, 1:].T, labels, colours):
            # print i,label,colour,
            # print colour
            # print i.shape,t.shape
            self.Fig1.draw_points(
                self.Data[::num, 0],
                i[::num],
                '.',
                Color=colour,
                Label=label
            )
            # self.Fig1.draw_line(t[::num],i[::num],'--',Color=colour,Label = label)
        self.Fig1.legend()
        self.Fig1.update()
        if e is not None:
            e.skip()


    def Bin_Data(self, data, BinAmount):

        if BinAmount == 1:
            return data
        # This is part of a generic binning class that I wrote.
        # It lets binning occur of the first axis for any 2D or 1D array
        if len(data.shape) == 1:
            data2 = zeros((data.shape[0] // BinAmount))
        else:
            data2 = zeros((data.shape[0] // BinAmount, data.shape[1]))

        for i in range(data.shape[0] // BinAmount):

            data2[i] = mean(data[i * BinAmount:(i + 1) * BinAmount], axis=0)

        return data2

    def onChar(self, event):
        # This function is for ensuring only numerical values are placed inside the textboxes
        key = event.GetKeyCode()

        # print ord(key)
        acceptable_characters = "1234567890."
        if key < 256 and key != 8:
            if chr(key) in acceptable_characters:
                event.Skip()
                return

            else:
                return False
        # This is for binding the F2 key to run
        elif key == 341:
            self.Run_Me(event)
            return
        else:
            event.Skip()
            return

    def Run_Me(self, event):
        # This function is for ensuring only numerical values are placed inside the textboxes
        key = event.GetKeyCode()

        if key == 341:
            self.Perform_Measurement(event)
        else:
            event.Skip()
            return

    def onChar_int(self, event):
        # This function is for ensuring only numerical values are placed inside the textboxes
        key = event.GetKeyCode()
        # print key
        # print ord(key)
        acceptable_characters = "1234567890"
        if key < 256 and key != 8:
            if chr(key) in acceptable_characters:
                event.Skip()
                return

            else:
                return False
        elif key == 341:
            self.Run_Me(event)
            return
        else:
            event.Skip()
            return

    def Num_Data_Points_Update(self, event):
        # what is the point of this function?
        getattr(self, 'GetValues_' + self.measurement_type)(event)
        time = self.Peroid + self.Offset_Before / 1000 + self.Offset_After / 1000

        self.m_DataPoint.SetValue('{0:.2e}'.format((time * float32(DAQmx_InputSampleRate) / self.Binning)[0]))

        self.m_Frequency.SetValue('{0:3.3f}'.format(1. / time))
        event.Skip()

    def CurrentLimits(self, event):
        # print self.m_Output.GetStringSelection(),self.m_Intensity.GetValue(),float(self.m_Intensity.GetValue())>1.5

        # This is function to determine the appropriate current limit for the box
        # A 10V limit is imposed oweing to limitations on the output voltage of the datcard
        try:
            if self.m_Output.GetStringSelection() == 'Low (50mA/V)':
                if float(self.m_Intensity.GetValue()) > 10:
                    # self.m_Intensity.SetBackgroundColour('RED')
                    self.m_Intensity.SetValue('10')
                # else:
                #     self.m_Intensity.SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ))
            # A 1.5V limit is imposed as a limit owing to the current limit of the power supply.
            elif self.m_Output.GetStringSelection() == 'High (2A/V)':

                if float(self.m_Intensity.GetValue()) > 1.5:
                    # self.m_Intensity.SetBackgroundColour('RED')
                    self.m_Intensity.SetValue('1.5')

            return False
        except:

            return False

    def CHK_Voltage_Threshold(self, Voltage_Threshold, event):
        if Voltage_Threshold > self.Intensity:
            if Voltage_Threshold > 66 * 5:
                self.m_Threshold.SetBackgroundColour('RED')
                event.Skip()
        else:
            self.m_Threshold.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

    def CHK_int(self, Textbox, event):
        try:
            return int(Textbox.GetValue())
            Textbox.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        except:
            Textbox.SetBackgroundColour('RED')
            event.Skip()

    def CHK_float(self, Textbox, event):
        try:
            # print Textbox.GetValue(),float(Textbox.GetValue())
            Textbox.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            return float(Textbox.GetValue())
        except:
            # print'yeah'
            Textbox.SetBackgroundColour('RED')

            event.Skip()
            return 0

if __name__ == "__main__":

    # mandatory in wx, create an app
    # False stands for not deteriction stdin/stdout
    # refer to manual for details
    app = wx.App(False)

    # create an object of CalcFrame
    frame = GUIController(None)
    frame.Show(True)
    # start the application
    app.MainLoop()
