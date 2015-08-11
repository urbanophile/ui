import json
import os  # importing wx files
import sys
import wx

import numpy as np
from util import utils
from hardware import daq
from Canvas import CanvasPanel
from DataPanel import DataPanel
from FrameSkeleton import FrameSkeleton  # import the newly created GUI file
from wx.lib.pubsub import pub
from ConfigParser import SafeConfigParser

# TODO: Remove when testing complete
from test.utils import make_sin_data


# Magic numbers relating to hardware. They convert sent voltage to current.
# They are determined by experimental measurement
HIGH_HARDWARD_CONST = 1840.
LOW_HARDWARE_CONST = 66.

# A 10V limit is imposed due to limited the output voltage of the datacard
LOW_VOLTAGE_LIMIT = 10

# A 1.5V limit is imposed as a limit owing to the current limit of
# the power supply.
HIGH_VOLTAGE_LIMIT = 1.5

# Constant that works, so the threshold doesn't get to big
THRESHOLD_CONST = 5

MAX_LOCALE_CHAR = 256


CHANNEL_INDEX = {
    'Reference': 1,
    'PC': 2,
    'PL': 3
}


class ExperimentSettings(object):
    """docstring for ExperimentSettings"""

    def __init__(self):
        super(ExperimentSettings, self).__init__()
        self.binning = 1
        self.averaging = 1
        self.channel = r'Low (50mA/V)'
        self.threshold = 150.0

        self.inverted_channels = {
            'Reference': True,
            'PC': False,
            'PL': True
        }
        self.sample_rate = np.float32(daq.DAQmx_InputSampleRate)
        self.InputVoltageRange = 10.0

        self.voltage_threshold = None
        self.channel_name = None


        self._determine_output_channel()

    def _determine_output_channel(self):
        # Just a simple function choosing the correct output channel
        # based on the drop down box
        if self.channel == 'High (2A/V)':
            self.channel_name = r'ao0'
            self.voltage_threshold = self.threshold / HIGH_HARDWARD_CONST
        elif self.channel == r'Low (50mA/V)':
            self.channel_name = r'ao1'
            self.voltage_threshold = self.threshold / LOW_HARDWARE_CONST

    def get_settings_as_dict(self):
        meta_data = {
            'Channel': self.channel,
            'Averaging': self.averaging,
            'Measurement_Binning': self.binning,
            'Threshold_mA': self.threshold,
            'inverted_channels': self.inverted_channels,
            'sample_rate': self.sample_rate
        }
        return meta_data


class ExperimentData(object):
    """docstring for ExperimentData"""
    def __init__(self, arg):
        super(ExperimentData, self).__init__()
        self.arg = arg


class AppController(object):
    """docstring for AppController"""
    def __init__(self, arg):
        super(AppController, self).__init__()
        self.arg = arg


class GUIController(FrameSkeleton):
    """
    Controller to handle interface with wx UI

    Attributes
    ----------


    MyFrame1:
    Fig1
    Data

    LoadPath
    Path
    measurement_type


    """

    def __init__(self, parent):

        # TODO: remove when finished testing data Transformations
        dat = make_sin_data()
        self.Data = None
        self.RawData = None

        self.metadata = ExperimentSettings()

        self.light_pulse = daq.LightPulse(
            waveform='Cos',
            amplitude=0.5,
            offset_before=1,
            offset_after=10,
            duration=1,
            voltage_threshold=150
        )

        self.measurement_handler = daq.MeasurementHandler(
            self.light_pulse.complete_waveform,
            self.metadata.averaging,
            self.metadata.channel_name,
            self.light_pulse.time_array[-1],
            self.metadata.InputVoltageRange
        )

        # setup file data
        self.dirname = os.getcwd()
        self.data_file = "untitled.dat"
        self.metadata_file = "untitled.inf"

        self._InitUI(parent)
        self._InitSubscriptions()
        self._InitValidators()

    def _InitUI(self, parent):
        # initialize parent class
        FrameSkeleton.__init__(self, parent)

        # setup Matplotlib Canvas panel
        self.Fig1 = CanvasPanel(self.Figure1_Panel)
        self.Fig1.labels('Raw Data', 'Time (s)', 'Voltage (V)')

        # make status bars
        m_statusBar = wx.StatusBar(self)

        self.SetStatusBar(m_statusBar)
        # self.m_statusBar.SetStatusText("Ready to go!")

        self.data_panel = DataProcessingPanel(self.m_notebook1)

        self.m_notebook1.AddPage(
            self.data_panel,
            u"Data Processing",
            True
        )

        # Setup the Menu
        menu_bar = wx.MenuBar()

        # File Menu
        filem = wx.Menu()
        filem.Append(wx.ID_OPEN, "Open\tCtrl+O")
        filem.Append(wx.ID_ANY, "Run\tCtrl+R")
        filem.Append(wx.ID_ABOUT, "About")
        filem.Append(wx.ID_EXIT, "Exit\tCtrl+X")

        # TODO: add and bind event handlers
        menu_bar.Append(filem, "&File")

        self.SetMenuBar(menu_bar)

    def _InitSubscriptions(self):
        # data transformations
        pub.subscribe(self.revertData, 'transform.revert')
        pub.subscribe(self.invertHandler, 'transform.invert')
        pub.subscribe(self.fftHandler, 'transform.fft')
        pub.subscribe(self.binHandler, 'transform.bin')
        pub.subscribe(self.offsetHandler, 'transform.offset')

        # plot changes
        pub.subscribe(self.onStatusUpdate, 'statusbar.update')
        pub.subscribe(self.plotHandler, 'update.plot')
        pub.subscribe(self.plotHandler, 'data.changed')

        # TODO initialise these views
        # widget views
        # pub.subscribe(self.setFrequency, 'waveform.changed')
        # pub.subscribe(self.setSampleDataPoints, 'settings.changed')
        # pub.subscribe(self.setPCCalibrationMean, 'pccalibration')
        # pub.subscribe(self.setPCCalibrationStd, 'pccalibration')



    def _InitValidators(self):

        # Waveform validators
        self.m_Intensity.SetValidator(NumRangeValidator(numeric_type='int'))
        self.m_Threshold.SetValidator(NumRangeValidator(numeric_type='int'))
        self.m_Period.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_Offset_Before.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_Offset_After.SetValidator(NumRangeValidator(numeric_type='float'))

        # Data collection validators
        self.m_samplingFreq.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_Averaging.SetValidator(NumRangeValidator(numeric_type='int'))
        self.m_Binning.SetValidator(NumRangeValidator(numeric_type='int'))

    #################################
    # Event Handlers for Measurements


    def Perform_Measurement(self, event):
        # all widgets are refreshed
        # A check is performed, and if failed, event is skipped

        self.onWaveformParameters(event)
        self.onCollectionParameters(event)
        print("GUIController: Perform_Measurement")
        # find what channel we are using, and what the voltage offset then is

        # This the event hasn't been skipped then continue with the code.
        self.m_scrolledWindow1.Refresh()
       
        print("GUIController: Perform_Measurement - event conditional")
        # Using that instance we then run the lights,
        # and measure the outputs
        raw_data = self.measurement_handler.Measure()
        self.Data = utils.bin_data(raw_data, self.metadata.binning)
        self.RawData = np.copy(self.Data)
        # We then plot the datas, this has to be changed if the plots want
        # to be updated on the fly.

        pub.sendMessage('update.plot')
        event.Skip()


    def onPCCalibration(self, event):
        pass


    ##########################
    # Error Handling functions

    def CurrentLimits(self, event):
        """
        Determines the appropriate current limit for the box
        """
        try:
            if self.m_Output.GetStringSelection() == 'Low (50mA/V)':
                if float(self.m_Intensity.GetValue()) > LOW_VOLTAGE_LIMIT:
                    self.m_Intensity.SetValue(str(LOW_VOLTAGE_LIMIT))

            elif self.m_Output.GetStringSelection() == 'High (2A/V)':

                if float(self.m_Intensity.GetValue()) > HIGH_VOLTAGE_LIMIT:
                    self.m_Intensity.SetValue(str(HIGH_VOLTAGE_LIMIT))

            return False
        except:

            return False


    def CHK_Voltage_Threshold(self, Voltage_Threshold, event):
        if Voltage_Threshold > self.Intensity:
            if Voltage_Threshold > LOW_HARDWARE_CONST * THRESHOLD_CONST:
                self.m_Threshold.SetBackgroundColour('RED')
                event.Skip()
        else:
            self.m_Threshold.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            )

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

    #################
    # Helper methods:


    def defaultFileDialogOptions(self):
        """
        Return a dictionary with file dialog options that can be
        used in both the save file dialog as well as in the open
        file dialog.
        """
        return dict(message='Choose a file', defaultDir=self.dirname, wildcard='*.*')

    def askUserForFilename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        if dialog.ShowModal() == wx.ID_OK:
            userProvidedFilename = True
            self.data_file = dialog.GetFilename()
            self.dirname = dialog.GetDirectory()
        else:
            userProvidedFilename = False
        dialog.Destroy()
        return userProvidedFilename

    ##########################
    # Model View Event Handlers
    #

    def onSamplingFreq(self, event):
        pass


    def onVoltageRange(self, event):
        pub.sendMessage('update.plot')

    def PlotData(self, e=None):

        self.Fig1.clear()
        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']

        print(self.Data.shape[0])
        print(self.Data)
        # this is done not to clog up the plot with many points
        if self.Data.shape[0] > 1000:
            num = self.Data.shape[0] // 1000
        else:
            num = 1

        # This plots the figure
        for i, label, colour in zip(self.Data[:, 1:].T, labels, colours):

            self.Fig1.draw_points(
                self.Data[::num, 0],
                i[::num],
                '.',
                Color=colour,
                Label=label
            )

        self.Fig1.legend()
        self.Fig1.update()
        if e is not None:
            e.skip()


    def Num_Data_Points_Update(self, event):
        """
        Updates main frame with estimated data point total and frequency
        """
        self.onWaveformParameters(self, event)
        self.onCollectionParameters(self, event)
        event.Skip()


    def onCollectionParameters(self, event):
        # TODO: refactor so it obeys DRY
        self.metadata.binning = self.CHK_int(self.m_Binning, event)
        self.metadata.averaging = self.CHK_int(self.m_Averaging, event)
        self.metadata.channel = self.m_Output.GetStringSelection()
        self.metadata.threshold = self.CHK_float(self.m_Threshold, event)
        self.metadata.sample_rate = self.CHK_float(self.m_samplingFreq, event)
        estimated_data = (self.light_pulse.time_array[-1] * self.metadata.sample_rate / self.metadata.binning)
        self.metadata.sample_data_points = estimated_data

        # pub.subscribe(self.setFrequency, 'waveform.changed')

    def onWaveformParameters(self, event):
        self.light_pulse.A = self.CHK_float(self.m_Intensity, event)
        self.light_pulse.Duration = self.CHK_float(self.m_Period, event)
        self.light_pulse.Offset_Before = self.CHK_float(self.m_Offset_Before, event)
        self.light_pulse.Offset_After = self.CHK_float(self.m_Offset_After, event)
        self.light_pulse.Waveform = self.m_Waveform.GetStringSelection()

        # pub.subscribe(self.setSampleDataPoints, 'settings.changed')

    def setPCCalibrationMean(self, pc_calibration_mean):
        pass

    def setPCCalibrationStd(self, pc_calibration_std):
        pass

    def setSampleDataPoints(self, sample_data_points):
        self.m_DataPoint.SetValue('{0:.2e}'.format(sample_data_points))

    def setFrequency(self, frequence_val):
        self.m_Frequency.SetValue('{0:3.3f}'.format(frequence_val))


    ##########################
    # App state Event Handlers
    #
    def onSave(self, event):
        """
        Method to handle dialogue window and saving data to file
        """
        self.onWaveformParameters(self, event)
        self.onCollectionParameters(self, event)


        dialog = wx.FileDialog(
            None,
            'Save measurement data and metadata',
            self.dirname,
            '',
            r'DAT and INF files (*.dat;*.inf)|*.inf;*.dat',
            wx.FD_SAVE
        )

        if dialog.ShowModal() == wx.ID_OK:
            dialog_path = dialog.GetPath()
            self.dirname = os.path.dirname(dialog_path)
            self.SaveName = os.path.splitext(os.path.basename(dialog_path))[0]

            metadata_dict = self.Make_List_For_Inf_Save(event)

            experiment_settings = self.metadata.get_settings_as_dict()
            waveform_settings = self.light_pulse.get_settings_as_dict()
            metadata_dict = experiment_settings.copy()

            utils.OutputData().save_data(self.Data, self.SaveName, self.dirname)
            utils.OutputData().save_metadata(
                metadata_dict,
                self.SaveName,
                self.dirname
            )

        else:
            print('Canceled save')
        dialog.Destroy()

        event.Skip()

    def onSaveData(self, event):
        pass


    def onLoad(self, event):
        """
        Method to handle load metadata dialog window and update metadata state
        """

        dialog = wx.FileDialog(
            None,
            'Select a metadata file',
            self.dirname,
            '',
            r'*.inf',
            wx.FD_OPEN
        )

        if dialog.ShowModal() == wx.ID_OK:

            metadata_dict = utils.OutputData().load_metadata(dialog.GetPath())
            metadata_stringified = dict(
                [a, str(x)] for a, x in metadata_dict.iteritems()
            )
            print(metadata_stringified)

            # experimental data
            self.m_Output.SetStringSelection(metadata_stringified[u'Channel'])
            self.m_Averaging.SetValue(metadata_stringified[u'Averaging'])
            try:
                self.m_Binning.SetValue(metadata_stringified[u'Measurement_Binning'])
            except:
                self.m_Binning.SetValue(metadata_stringified[u'Binning'])
            self.m_Threshold.SetValue(metadata_stringified[u'Threshold_mA'])


            # waveform data
            self.m_Intensity.SetValue(metadata_stringified[u'Intensity_v'])
            self.m_Waveform.SetStringSelection(metadata_stringified[u'Waveform'])

            self.m_Offset_Before.SetValue(metadata_stringified[u'Offset_Before_ms'])
            self.m_Offset_After.SetValue(metadata_stringified[u'Offset_After_ms'])
            self.m_Period.SetValue(metadata_stringified[u'Peroid_s'])

        dialog.Destroy()
        event.Skip()

    def onLoadData(self, event):
        """
        Handlers loading of new data set into Frame
        """
        print("start data loading")
        if self.askUserForFilename(style=wx.OPEN,
                                   **self.defaultFileDialogOptions()):
            fullpath = os.path.join(self.dirname, self.data_file)
            self.Data = utils.OutputData().load_data(fullpath)
            self.RawData = np.copy(self.Data)

            print(self.Data)
            pub.sendMessage('update.plot')
            self.Num_Data_Points_Update(event)

    def onExit(self, event):
        self.Close()

    def OnAbout(self, event):
        dialog = wx.MessageDialog(
            self,
            'An PV experimental assistant in wxPython',
            'About PVapp',
            wx.OK
        )
        dialog.ShowModal()
        dialog.Destroy()


    def onStatusUpdate(self, status, is_error=False):

        self.SetStatusText(status, 0)
        if is_error:
            self.m_statusBar.SetBackgroundColour('RED')
            self.m_statusBar.SetStatusText(status)
        else:
            self.m_statusBar.SetStatusText(status)

    def plotHandler(self):
        self.PlotData()

    def onDetermineOffset(self, event):
        """
        Opens custom dialog box with interactive offset determination
        """
        if self.Data is not None:
            title = 'Determine offset interactively'
            chgdep = ChangeDepthDialog(None, title=title)
            chgdep.ShowModal()
            chgdep.Destroy()
        else:
            pub.sendMessage(
                'statusbar.update',
                'No data available',
                error=True)

    ####################################
    # Data Transformation Event Handlers
    #

    def revertData(self):
        self.Data = np.copy(self.RawData)
        pub.sendMessage('data.changed')


    def invertHandler(self, channel):
        self.Data[:, CHANNEL_INDEX[channel]] *= -1
        self.metadata.inverted_channels[channel] = not self.metadata.inverted_channels[channel]
        pub.sendMessage('data.changed')

    def offsetHandler(self, offset_type=None, offset=None, channel=None):
        if offset_type == 'y':
            index = CHANNEL_INDEX[channel]
            self.Data[:, index] = self.Data[:, index] + offset
        elif offset_type == 'start_x':
            self.Data = self.Data[self.Data[:, 0] > offset, :]
        elif offset_type == 'end_x':
            # so this isn't cumulative
            offset = self.RawData[-1, 0] - offset
            self.Data = self.Data[self.Data[:, 0] < offset, :]
        pub.sendMessage('data.changed')


    def fftHandler(self, offset_type, distance):
        pass

    def binHandler(self, bin_size):
        self.Data = utils.bin_data(self.Data, bin_size)
        pub.sendMessage('data.changed')



class DataProcessingPanel(DataPanel):

    def __init__(self, parent):
        # initialize parent class
        DataPanel.__init__(self, parent)

        self.m_yChannelChoice.AppendItems(['Reference', 'PC', 'PL'])

        self.m_startXOffset.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_endXOffset.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_yOffset.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_binSize.SetValidator(NumRangeValidator())

    #################
    # UI listeners

    def setDataPoints(self, num_data_points):
        self.m_DataPoints.SetValue(str(num_data_points))

    def setWaveform(self, waveform_name):
        self.m_Waveform.SetValue(str(money))

    def setFrequency(self, frequence_val):
        self.m_Frequency.SetValue(str(frequence_val))

    def setIntensity(self, intensity_val):
        self.m_Intensity.SetValue(str(intensity_val))

    #################
    # Event handlers

    def onBinData(self, event):
        num = int(self.m_binSize.GetValue())
        pub.sendMessage('transform.bin', bin_size=num)

    def onFourierTransform(self, event):
        pub.sendMessage('transform.fft')

    def onRevertData(self, event):
        pub.sendMessage('transform.revert')

    def onOffset(self, event):
        start_x_num = float(self.m_startXOffset.GetValue())
        end_x_num = float(self.m_endXOffset.GetValue())
        y_num = float(self.m_yOffset.GetValue())
        channel = self.m_yChannelChoice.GetStringSelection()

        pub.sendMessage('transform.offset', offset_type='start_x', offset=start_x_num, channel='all')
        pub.sendMessage('transform.offset', offset_type='end_x', offset=end_x_num, channel='all')
        pub.sendMessage('transform.offset', offset_type='y', offset=y_num, channel=channel)

    def onInvertReference(self, event):
        pub.sendMessage('transform.invert', channel='Reference')

    def onInvertPC(self, event):
        pub.sendMessage('transform.invert', channel='PC')

    def onInvertPL(self, event):
        pub.sendMessage('transform.invert', channel='PL')



class ChangeDepthDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(ChangeDepthDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Offsets")


    def InitUI(self):

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.RadioButton(pnl, label='Custom'))
        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)

        tc_x_start = wx.TextCtrl(self, style=TE_READONLY)
        tc_y_start = wx.TextCtrl(self, style=TE_READONLY)
        tc_x_end = wx.TextCtrl(self, style=TE_READONLY)
        tc_y_end = wx.TextCtrl(self, style=TE_READONLY)

        x_start_label = wx.StaticText(self, 'x:')
        y_start_label = wx.StaticText(self, 'y:')

        x_end_label = wx.StaticText(self, 'x:')
        y_end_label = wx.StaticText(self, 'y:')

        sb_start = wx.StaticBox(panel, label="Initial Offset")
        boxsizer_start = wx.StaticBoxSizer(sb, wx.VERTICAL)

        sb_end = wx.StaticBox(panel, label="Final Offset")
        boxsizer_end = wx.StaticBoxSizer(sb, wx.VERTICAL)

        sb_start.Add(tc_x_start)
        sb_start.Add(tc_x_start)

        panel.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2,
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        # event handlers
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):
        self.Destroy()


class NumRangeValidator(wx.PyValidator):
    """
    Numeric Validator for a TextCtrl
    """

    def __init__(self, numeric_type='int', min_=0, max_=sys.maxint):
        super(NumRangeValidator, self).__init__()
        print(numeric_type)
        if numeric_type == 'int':
            assert min_ >= 0
        self._min = min_
        self._max = max_
        self.numeric_type = numeric_type
        if numeric_type == 'int':
            self.convert_to_num = int
            self.allow_chars = "-1234567890"
            self.is_num = lambda x: x.isdigit()
        elif numeric_type == 'float':
            self.convert_to_num = float
            self.allow_chars = "+-.e1234567890"
            self.is_num = utils.is_float

        # Event management
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """Require override"""
        return NumRangeValidator(self._min, self._max, self.numeric_type)

    def Validate(self, win):
        """
        Override to validate window's value
        Return: Boolean
        """
        txtCtrl = self.GetWindow()
        val = txtCtrl.GetValue()
        isValid = False
        if self.is_num(val):
            digit = self.convert_to_num(val)
            if digit >= self._min and digit <= self._max:
                isValid = True

        if not isValid:
            message = 'Data must be {0} between {1} and {2}'.format(
                self.numeric_type,
                self._min,
                self._max
            )
            pub.sendMessage(
                'statusbar.update',
                message,
                error=True
            )
            return isValid

    def OnChar(self, event):
        txtCtrl = self.GetWindow()
        key = event.GetKeyCode()
        isDigit = False
        if key < 256:
            isValid = chr(key) in self.allow_chars
        if key in (wx.WXK_RETURN, wx.WXK_DELETE, wx.WXK_BACK) or key > 255 or isValid:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            # Beep to warn about invalid input
            wx.Bell()
        return

    def TransferToWindow(self):
        """Overridden to skip data transfer"""
        return True

    def TransferFromWindow(self):
        """Overridden to skip data transfer"""
        return True
