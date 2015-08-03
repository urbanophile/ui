import wx
import os  # importing wx files
from Canvas import CanvasPanel
import Gui_Main_v2 as gui  # import the newly created GUI file
from util import utils
from hardware import daq
import numpy as np


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

# ##### EVENT BINDINGS
# self.m_scrolledWindow1.Bind( wx.EVT_CHAR, self.Run_Me )
# self.m_Intensity.Bind( wx.EVT_CHAR, self.onChar )
# self.m_Intensity.Bind( wx.EVT_TEXT, self.CurrentLimits )
# self.m_Output.Bind( wx.EVT_CHOICE, self.CurrentLimits )
# self.m_Period.Bind( wx.EVT_CHAR, self.onChar )
# self.m_Period.Bind( wx.EVT_KILL_FOCUS, self.Num_Data_Points_Update )
# self.m_Offset_Before.Bind( wx.EVT_CHAR, self.onChar )
# self.m_Offset_Before.Bind( wx.EVT_KILL_FOCUS, self.Num_Data_Points_Update )
# self.m_Offset_After.Bind( wx.EVT_CHAR, self.onChar )
# self.m_Offset_After.Bind( wx.EVT_KILL_FOCUS, self.Num_Data_Points_Update )
# self.m_Averaging.Bind( wx.EVT_CHAR, self.onChar_int )
# self.m_Binning.Bind( wx.EVT_CHAR, self.onChar_int )
# self.m_Binning.Bind( wx.EVT_KILL_FOCUS, self.Num_Data_Points_Update )
# self.GoButton.Bind( wx.EVT_BUTTON, self.Perform_Standard_Measurement )
# self.m_Save.Bind( wx.EVT_BUTTON, self.Save )
# self.m_Load.Bind( wx.EVT_BUTTON, self.Load )
# self.ChkBox_Ref.Bind( wx.EVT_CHECKBOX, self.PlotData )
# self.ChkBox_PC.Bind( wx.EVT_CHECKBOX, self.PlotData )
# self.ChkBox_PL.Bind( wx.EVT_CHECKBOX, self.PlotData )


# self.Waveform = waveform
# self.A = amplitude
# self.Offset_Before = offset_before
# self.Offset_After = offset_after
# self.Duration = duration
# self.output_samples = sample_frequency
# self.Voltage_Threshold = voltage_threshold
# self.time_array = np.array([])

class ExperimentSettings(object):
    """docstring for ExperimentSettings"""

    def __init__(self, binning, averaging, channel):
        super(ExperimentSettings, self).__init__()
        self.binning = binning
        self.averaging = averaging
        self.channel = channel
        self.inverted_chanels = {}


class GUIController(gui.MyFrame1):
    """
    Controller to handle interface with wx UI

    Attributes
    ----------
    Threshold:
    Channel:
    MyFrame1:
    Fig1
    Data

    LoadPath
    Path
    measurement_type


    Intensity
    Binning
    Averaging
    Peroid
    Offset_Before
    Offset_After
    Waveform
    Channel
    Threshold
    """
    # constructor
    measurement_type = 'Standard'

    def __init__(self, parent):
        # initialize parent class
        gui.MyFrame1.__init__(self, parent)

        self.Fig1 = CanvasPanel(self.Figure1_Panel)
        self.Fig1.labels('Raw Data', 'Time (s)', 'Voltage (V)')

        self.Data = np.array([])
        self.metadata = None
        self.Waveform = None
        # CanvasPanel(self.Figure2_Panel)
        self.dirname = os.getcwd()
        self.data_file = "untitled.dat"
        self.metadata_file = "untitled.inf"

    def Determine_Digital_Output_Channel(self):
        # Just a simple function choosing the correct output channel
        # based on the drop down box
        if self.Channel == 'High (2A/V)':
            Channel = r'ao0'
            # 1840 comes from exp measurements
            Voltage_Threshold = self.Threshold / HIGH_HARDWARD_CONST
        elif self.Channel == r'Low (50mA/V)':
            Channel = r'ao1'
            # 66 comes from experimental measurements
            Voltage_Threshold = self.Threshold / LOW_HARDWARE_CONST
            # apparently this is an equiptment thing
        print(self.Channel, self.Channel == r'Low (50mA/V)')

        return Channel, Voltage_Threshold

    def Save(self, event):
        """
        Method to handle dialogue window and saving data to file
        """
        self.GetValues_Standard(event)

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

            metadata_list = self.Make_List_For_Inf_Save(event)

            utils.OutputData().save_data(self.Data, self.SaveName, self.dirname)
            utils.OutputData().save_metadata(
                metadata_list,
                self.SaveName,
                self.dirname
            )

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

            # waveform data
            self.m_Intensity.SetValue(metadata_stringified[u'Intensity_v'])
            self.m_Threshold.SetValue(metadata_stringified[u'Threshold_mA'])
            self.m_Waveform.SetStringSelection(metadata_stringified[u'Waveform'])


            self.m_Offset_Before.SetValue(metadata_stringified[u'Offset_Before_ms'])
            self.m_Offset_After.SetValue(metadata_stringified[u'Offset_After_ms'])
            self.m_Period.SetValue(metadata_stringified[u'Peroid_s'])

        dialog.Destroy()
        event.Skip()

    # rename to
    def GetValues_Standard(self, event):

        # TODO: refactor so it obeys DRY
        self.Binning = self.CHK_int(self.m_Binning, event)
        self.Averaging = self.CHK_int(self.m_Averaging, event)
        self.Channel = self.m_Output.GetStringSelection()

        self.Intensity = self.CHK_float(self.m_Intensity, event)
        self.Peroid = self.CHK_float(self.m_Period, event)
        self.Offset_Before = self.CHK_float(self.m_Offset_Before, event)
        self.Offset_After = self.CHK_float(self.m_Offset_After, event)
        self.Waveform = self.m_Waveform.GetStringSelection()
        self.Threshold = self.CHK_float(self.m_Threshold, event)

    def Make_List_For_Inf_Save(self, event):

        Channel = self.m_Output.GetStringSelection()
        Averaging = self.CHK_int(self.m_Averaging, event)
        Measurement_Binning = self.CHK_int(self.m_Binning, event)

        Intensity_v = self.CHK_float(self.m_Intensity, event)
        Threshold_mA = self.CHK_float(self.m_Threshold, event)
        Waveform = self.m_Waveform.GetStringSelection()
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

        self.GetValues_Standard(event)

        # find what channel we are using, and what the voltage offset then is
        Channel, Voltage_Threshold = self.Determine_Digital_Output_Channel()

        self.CHK_Voltage_Threshold(Voltage_Threshold, event)

        # This the event hasn't been skipped then continue with the code.
        self.m_scrolledWindow1.Refresh()
        if not event.GetSkipped():

            #  Then the light pulse is defined, but the lightpulse class
            light_pulse = daq.LightPulse(
                self.Waveform,
                self.Intensity,  # intensity is amplitude
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
            Go = daq.TakeMeasurements(
                light_pulse.complete_waveform,
                self.Averaging,
                Channel,
                light_pulse.t[-1]
            )

            # print 'here'
            # Using that instance we then run the lights,
            # and measure the outputs
            self.Data = utils.bin_data(Go.Measure(), self.Binning)
            # self.Data = lightPulse.Define()
            # We then plot the datas, this has to be changed if the plots want
            # to be updated on the fly.

            event.Skip()
        else:

            self.m_scrolledWindow1.Refresh()

    def PlotData(self, e=None):

        self.Fig1.clear()
        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']

        print(self.Data.shape)
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

    def charValidator(self, event, acceptable_characters):
        """
        Ensures only acceptable_characters values are placed inside textboxes
        """
        key = event.GetKeyCode()

        # key is in 8bit character set and isn't back
        if key < MAX_LOCALE_CHAR and key != wx.WXK_BACK:
            if chr(key) in acceptable_characters:
                event.Skip()
                return

            else:
                return False

        # This is for binding the F2 key to run
        elif key == wx.WXK_F2:
            self.Run_Me(event)
            return
        else:
            event.Skip()
            return

    def onChar(self, event):
        self.charValidator(event, "1234567890.")

    def onChar_int(self, event):
        self.charValidator(event, "1234567890")



    def Run_Me(self, event):
        # This function is for ensuring only numerical values are placed inside the textboxes
        key = event.GetKeyCode()

        if key == wx.WXK_F2:
            self.Perform_Measurement(event)
        else:
            event.Skip()
            return



    def Num_Data_Points_Update(self, event):
        """
        Updates main frame with new data point total
        """
        self.GetValues_Standard(event)
        time = self.Peroid + self.Offset_Before / 1000 + self.Offset_After / 1000
        num_data = (time * np.float32(daq.DAQmx_InputSampleRate) / self.Binning)[0]
        self.m_DataPoint.SetValue('{0:.2e}'.format(num_data))

        self.m_Frequency.SetValue('{0:3.3f}'.format(1. / time))
        event.Skip()

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

    ##########################
    # Error Handling functions

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

    ################
    # Event Handlers
    #
    def onLoadData(self, event):
        """
        Handlers loading of new data set into Frame
        """
        print("start data loading")
        if self.askUserForFilename(style=wx.OPEN,
                                   **self.defaultFileDialogOptions()):
            fullpath = os.path.join(self.dirname, self.data_file)
            self.Data = utils.OutputData().load_data(fullpath)

            print(self.Data)
            self.PlotData()
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

    def onInvert(self, event):
        """
        Inverts data based on channel inputs
        """
        if self.ChkBox_PL.GetValue():
            self.Data[:, 3] *= -1
        if self.ChkBox_PC.GetValue():
            self.Data[:, 2] *= -1

        if self.ChkBox_Ref.GetValue():
            self.Data[:, 1] *= -1
            print(self.Data[1, 1], )
            print('\n ref ')

        self.PlotData(event)
