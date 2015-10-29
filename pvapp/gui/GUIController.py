import os  # importing wx files
import wx
import copy
import numpy as np
from util import utils
from util.Constants import (
    CHANNELS,
    CHANNEL_INDEX,
    INPUT_VOLTAGE_RANGE_STR,
    WAVEFORMS,
    OUTPUTS
)
from hardware import daq
from hardware.MeasurementHandler import MeasurementHandler
from Canvas import CanvasPanel
from DataPanel import DataPanel
from Validator import NumRangeValidator
from models.ExperimentData import ExperimentData
from models.ExperimentSettings import ExperimentSettings

from FrameSkeleton import FrameSkeleton  # import the newly created GUI file
from wx.lib.pubsub import pub


class PVapp(wx.App):
    """docstring for PVapp"""
    def OnInit(self):
        self.legacy_view = GUIController(None)
        self.legacy_view.Show()

        self.controller = PlaceholderController(self.legacy_view)

        self.data_panel_controller = DataPanelHandler(
            self.legacy_view.Data,
            self.legacy_view.data_panel,
            self.legacy_view
        )
        return True


class PlaceholderController(object):
    """A transitional class for controller methods"""
    def __init__(self, legacy_view):
        super(PlaceholderController, self).__init__()
        self.view = legacy_view
        self.__InitHandlers()
        self.__InitSubscriptions()

    def __InitHandlers(self):
        # Connect Events waveform parameters
        self.view.m_Intensity.Bind(wx.EVT_KILL_FOCUS, self.view.onWaveformParameters)
        self.view.m_Period.Bind(wx.EVT_KILL_FOCUS, self.view.onWaveformParameters)
        self.view.m_Offset_Before.Bind(wx.EVT_KILL_FOCUS, self.view.onWaveformParameters)
        self.view.m_Offset_After.Bind(wx.EVT_KILL_FOCUS, self.view.onWaveformParameters)
        self.view.m_Threshold.Bind(wx.EVT_KILL_FOCUS, self.view.onWaveformParameters)

        self.view.m_Output.Bind(wx.EVT_CHOICE, self.view.onWaveformParameters)
        self.view.m_Waveform.Bind(wx.EVT_CHOICE, self.view.onWaveformParameters)

        # data collection parameters
        self.view.m_samplingFreq.Bind(wx.EVT_KILL_FOCUS, self.view.onCollectionParameters)
        self.view.m_Binning.Bind(wx.EVT_KILL_FOCUS, self.view.onCollectionParameters)

        self.view.m_voltageRange.Bind(wx.EVT_CHOICE, self.view.onCollectionParameters)

        # measurement events
        self.view.m_Measure.Bind(wx.EVT_BUTTON, self.view.Perform_Measurement)
        self.view.m_PCCalibration.Bind(wx.EVT_BUTTON, self.onPCCalibration)

        # save events
        self.view.m_Save.Bind(wx.EVT_BUTTON, self.view.onSave)
        self.view.m_SaveData.Bind(wx.EVT_BUTTON, self.view.onSaveData)
        self.view.m_Load.Bind(wx.EVT_BUTTON, self.view.onLoad)
        self.view.m_LoadData.Bind(wx.EVT_BUTTON, self.view.onLoadData)

    def __InitSubscriptions(self):

        # data transformations
        pub.subscribe(self.view.Data.revertData, 'transform.revert')
        pub.subscribe(self.view.Data.invertHandler, 'transform.invert')
        pub.subscribe(self.view.fftHandler, 'transform.fft')
        pub.subscribe(self.view.Data.binHandler, 'transform.bin')
        pub.subscribe(self.view.Data.offsetHandler, 'transform.offset')

        # plot changes
        pub.subscribe(self.view.onStatusUpdate, 'statusbar.update')
        pub.subscribe(self.view.plotHandler, 'update.plot')
        pub.subscribe(self.view.plotHandler, 'data.changed')

        # UPDATE write only textboxes
        # pub.subscribe(self.view.setPCCalibrationMean, 'calibration.pc')
        # pub.subscribe(self.view.setPCCalibrationStd, 'calibration.pc')

        pub.subscribe(self.view.setWaveformParameters, 'waveform.change')
        pub.subscribe(self.view.setCollectionParameters, 'collection.change')

        # UPDATE Data Panel displayed views
        pub.subscribe(self.updateDataPanelFixed, 'waveform.change')
        pub.subscribe(self.updateDataPanelFixed, 'collection.change')

        pub.subscribe(self.listener, 'collection')
        pub.subscribe(self.listener, 'transform')
        pub.subscribe(self.listener, 'data')
        pub.subscribe(self.listener, 'update')


    def listener(self, message=pub.AUTO_TOPIC):
        print("message heard: {0}".format(message))
        # self.view.onStatusUpdate(str(message))

    def updateDataPanelFixed(self):
        self.view.data_panel.setDataPoints(
            self.view.metadata.get_total_data_points()
        )
        self.view.data_panel.setWaveform(
            self.view.metadata.waveform
        )
        self.view.data_panel.setFrequency(
            self.view.metadata.get_frequency()
        )
        self.view.data_panel.setAmplitude(
            self.view.metadata.amplitude
        )

    def onPCCalibration(self, event):
        print('onPCCalibration')
        self.view.ShowCalibrationModal()

        null_metadata = copy.deepcopy(self.view.metadata)
        null_metadata.waveform = "NullWave"
        null_metadata.averaging = 1

        null_pulse = daq.LightPulse(null_metadata)

        # Using that instance we then run the lights,
        # and measure the outputs
        measurement_handler = MeasurementHandler()
        measurement_handler.add_to_queue(
            null_pulse.complete_waveform,
            null_metadata
        )

        calibration_data = measurement_handler.single_measurement()
        self.view.metadata.pc_calibration.update_data(calibration_data)
        # We then plot the datas, this has to be changed if the plots want
        # to be updated on the fly.

        pub.sendMessage('calibration.pc')






# hybrid view/controller
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

        # models
        self.metadata = ExperimentSettings()

        self.Data = ExperimentData(metadata=self.metadata)

        self.light_pulse = daq.LightPulse(self.metadata)

        # setup file data
        self.dirname = os.getcwd()
        self.data_file = "untitled.dat"
        self.metadata_file = "untitled.inf"

        self.__InitUI(parent)
        self.__InitValidators()

    def __InitUI(self, parent):
        # initialize parent class
        FrameSkeleton.__init__(self, parent)

        # setup Matplotlib Canvas panel
        self.Fig1 = CanvasPanel(self.Figure1_Panel)

        # make status bars
        m_statusBar = wx.StatusBar(self)

        self.SetStatusBar(m_statusBar)
        # self.m_statusBar.SetStatusText("Ready to go!")

        self.data_panel = DataProcessingPanel(self.m_notebook1)

        self.m_notebook1.AddPage(
            self.data_panel,
            u"Data Processing",
            # True
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

        # initialise view with model parameters
        self.m_voltageRange.AppendItems(INPUT_VOLTAGE_RANGE_STR)
        self.m_Waveform.AppendItems(WAVEFORMS)
        self.m_Output.AppendItems(OUTPUTS)

        self.setWaveformParameters()
        self.setCollectionParameters()

    def __InitValidators(self):

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

    def setPCCalibrationMean(self):
        self.m_pcCalibrationMean.SetValue('{0:3.3f}'.format(
            self.metadata.pc_calibration_mean
        ))

    def setPCCalibrationStd(self):
        self.m_pcCalibrationStd.SetValue('{0:3.3f}'.format(
            self.metadata.pc_calibration_std
        ))

    def setSampleDataPoints(self, sample_data_points):
        self.m_DataPoint.SetValue('{0:.2e}'.format(sample_data_points))

    def setFrequency(self, frequence_val):
        self.m_Frequency.SetValue('{0:3.3f}'.format(frequence_val))

    def setWaveformParameters(self):
        self.m_Intensity.SetValue(str(self.metadata.amplitude))
        self.m_Period.SetValue(str(self.metadata.duration))
        self.m_Offset_Before.SetValue(str(self.metadata.offset_before))
        self.m_Offset_After.SetValue(str(self.metadata.offset_after))
        self.setFrequency(self.metadata.get_frequency())

    def setCollectionParameters(self):
        self.m_Binning.SetValue(str(self.metadata.binning))
        self.m_Averaging.SetValue(str(self.metadata.averaging))
        self.m_Threshold.SetValue(str(self.metadata.threshold))
        self.m_samplingFreq.SetValue(str(self.metadata.sample_rate))

        self.setSampleDataPoints(self.metadata.get_total_data_points())


    #################################
    # Event Handlers for Measurements
    def Perform_Measurement(self, event):

        print("GUIController: Perform_Measurement")

        # Using that instance we then run the lights,
        # and measure the outputs
        self.measurement_handler = MeasurementHandler()
        measurement_handler.add_to_queue(
            self.light_pulse.complete_waveform,
            self.metadata
        )

        raw_data = self.measurement_handler.single_measurement()
        self.Data.updateRawData(raw_data)
        self.Data.Data = utils.bin_data(raw_data, self.metadata.binning)
        # We then plot the datas, this has to be changed if the plots want
        # to be updated on the fly.

        pub.sendMessage('update.plot')


    def fftHandler(self):
        channel = self.data_panel.m_fftChoice.GetStringSelection()
        freq_data = self.Data.fftOperator(channel, self.metadata.get_total_time())
        self.PlotData(freq_data, title=['FFT of Raw data', 'Frequency (hz)', 'Voltage (V)'])


    def onWaveformParameters(self, event):
        self.metadata.A = float(self.m_Intensity.GetValue())
        self.metadata.Duration = float(self.m_Period.GetValue())
        self.metadata.Offset_Before = float(self.m_Offset_Before.GetValue())
        self.metadata.Offset_After = float(self.m_Offset_After.GetValue())
        self.metadata.Waveform = self.m_Waveform.GetStringSelection()

        pub.sendMessage('waveform.change')


    def onCollectionParameters(self, event):
        # TODO: refactor so it obeys DRY

        self.metadata.binning = int(self.m_Binning.GetValue())
        self.metadata.averaging = int(self.m_Averaging.GetValue())
        self.metadata.channel = self.m_Output.GetStringSelection()
        self.metadata.threshold = float(self.m_Threshold.GetValue())
        self.metadata.sample_rate = float(self.m_samplingFreq.GetValue())
        self.metadata.sample_data_points = self.metadata.get_total_data_points()

        pub.sendMessage('collection.change')

    ##########################
    # Plot Handlers
    #

    def plotHandler(self):
        self.PlotData(self.Data.Data)

    def PlotData(self, data, data_labels=['Reference', 'PC', 'PL'],
                 title=['Raw Data', 'Time (s)', 'Voltage (V)'], e=None):

        self.Fig1.clear()
        labels = data_labels
        colours = ['b', 'r', 'g']

        # this is done not to clog up the plot with many points
        if data.shape[0] > 1000:
            num = data.shape[0] // 1000
        else:
            num = 1

        # This plots the figure
        for i, label, colour in zip(data[:, 1:].T, labels, colours):

            self.Fig1.draw_points(
                data[::num, 0],
                i[::num],
                '.',
                Color=colour,
                Label=label
            )

        self.Fig1.legend()
        self.Fig1.labels(title[0], title[1], title[2])
        self.Fig1.update()
        if e is not None:
            e.skip()

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

    def ShowCalibrationModal(self):
        msg_text = (
            "Please remove sample from measurement area\n"
            "Only one PC calibration is necessary per experimental session"
        )
        wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)

    ##########################
    # App state Event Handlers
    #
    def onSave(self, event):
        """
        Method to handle dialogue window and saving data to file
        """

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

            experiment_settings = self.metadata.get_settings_as_dict()
            waveform_settings = self.light_pulse.get_settings_as_dict()
            metadata_dict = experiment_settings.copy()

            utils.save_data(self.Data.Data, self.SaveName, self.dirname)
            utils.save_metadata(
                metadata_dict,
                self.SaveName,
                self.dirname
            )

        else:
            print('Canceled save')
        dialog.Destroy()

        event.Skip()

    def onSaveData(self, event):
        print("onSaveData")
        if self.askUserForFilename(style=wx.SAVE,
                                   **self.defaultFileDialogOptions()):
            utils.save_data(self.Data.Data, self.data_file, self.dirname)

        # print(filename)
        # fullpath = os.path.join(self.dirname, self.data_file)
        # self.Data.updateRawData(utils.load_data(fullpath))


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

            metadata_dict = utils.load_metadata(dialog.GetPath())
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
            self.Data.updateRawData(utils.load_data(fullpath))

            print(self.Data.Data)
            pub.sendMessage('update.plot')
            self.onWaveformParameters(self, event)
            self.onCollectionParameters(self, event)

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

    # def onDetermineOffset(self, event):
    #     """
    #     Opens custom dialog box with interactive offset determination
    #     """
    #     if self.Data.Data is not None:
    #         title = 'Determine offset interactively'
    #         chgdep = ChangeDepthDialog(None, title=title)
    #         chgdep.ShowModal()
    #         chgdep.Destroy()
    #     else:
    #         pub.sendMessage(
    #             'statusbar.update',
    #             'No data available',
    #             error=True)


class DataProcessingPanel(DataPanel):

    def __init__(self, parent):
        self.SLIDER_MIN = 0
        self.SLIDER_MAX = 100
        self.SLIDER_INITIAL = 100

        # initialize parent class
        DataPanel.__init__(self, parent)

        self.__InitLayout()

    def __InitLayout(self):
        self.m_OffsetSlider.SetRange(self.SLIDER_MIN, self.SLIDER_MAX)
        self.m_OffsetSlider.SetValue(self.SLIDER_MAX)

        self.m_offsetChannelChoice.AppendItems(CHANNELS)
        self.m_fftChoice.AppendItems(CHANNELS)

        self.m_leftCropDistance.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_rightCropDistance.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_yOffset.SetValidator(NumRangeValidator(numeric_type='float'))
        self.m_binSize.SetValidator(NumRangeValidator())


    #################
    # UI listeners

    def setDataPoints(self, num_data_points):
        self.m_DataPoints.SetValue(str(num_data_points))

    def setWaveform(self, waveform_name):
        self.m_Waveform.SetValue(str(waveform_name))

    def setFrequency(self, frequence_val):
        self.m_Frequency.SetValue(str(frequence_val))

    def setAmplitude(self, intensity_val):
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
        pub.sendMessage('data.changed')

    def onCrop(self, event):
        start_x_num = float(self.m_leftCropDistance.GetValue())
        end_x_num = float(self.m_rightCropDistance.GetValue())
        pub.sendMessage('transform.offset', offset_type='start_x', offset=start_x_num, channel='all')
        pub.sendMessage('transform.offset', offset_type='end_x', offset=end_x_num, channel='all')

    def onOffset(self, event):
        """ Offset should be determined as mean over selected period"""
        y_num = float(self.m_yOffset.GetValue())
        channel = self.m_yChannelChoice.GetStringSelection()
        pub.sendMessage('transform.offset', offset_type='y', offset=y_num, channel=channel)

    def onInvertReference(self, event):
        pub.sendMessage('transform.invert', channel='Reference')
        pub.sendMessage('data.changed')

    def onInvertPC(self, event):
        pub.sendMessage('transform.invert', channel='PC')
        pub.sendMessage('data.changed')

    def onInvertPL(self, event):
        pub.sendMessage('transform.invert', channel='PL')
        pub.sendMessage('data.changed')


class DataPanelHandler(object):
    """docstring for DataPanelHandler"""
    def __init__(self, data, datapanel_view, acquisition_view):
        super(DataPanelHandler, self).__init__()

        self.HEIGHT = 2

        self.Data = data
        self.datapanel = datapanel_view
        self.acquisition_view = acquisition_view
        self.axes1 = self.acquisition_view.Fig1.axes
        self.figure_canvas = self.acquisition_view.Fig1.canvas
        self.__InitHandlers()
        self.__PlotHandler()

    def __InitHandlers(self):
        self.datapanel.m_OffsetSlider.Bind(wx.EVT_SLIDER, self.onSliderScroll)

        self.datapanel.m_changeOffset.Bind(wx.EVT_BUTTON, self.onChangeOffset)
        self.datapanel.m_interactiveOffsets.Bind(wx.EVT_BUTTON, self.onInteractiveOffsets)

    def __PlotHandler(self):
        x = [self.datapanel.SLIDER_INITIAL] * self.HEIGHT
        y = range(self.HEIGHT)

        # matplotlib canvas

        # TODO refactor
        self.figure_canvas.line, = self.axes1.plot(x, y, linewidth=2)

        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']
        data = self.Data.Data
        for i, label, colour in zip(data[:, 1:].T, labels, colours):

            self.axes1.plot(
                data[::1, 0],
                i[::1],
                '.',
                color=colour,
                # Label=label
            )

    def onChangeOffset(self, event):
        num = float(self.datapanel.m_yOffset.GetValue())
        channel = self.datapanel.m_offsetChannelChoice.GetStringSelection()
        self.Data.Data[:, CHANNEL_INDEX[channel]] = self.Data.Data[:, CHANNEL_INDEX[channel]] - num

    def onInteractiveOffsets(self, event):
        val = self.datapanel.m_OffsetSlider.GetValue()
        num = self.offset_mean(val, 1)
        channel = self.datapanel.m_offsetChannelChoice.GetStringSelection()
        self.Data.Data[:, CHANNEL_INDEX[channel]] = self.Data.Data[:, CHANNEL_INDEX[channel]] - num

    def onSliderScroll(self, event):
        channel = self.datapanel.m_offsetChannelChoice.GetStringSelection()
        index = CHANNEL_INDEX[channel]

        obj = event.GetEventObject()
        val = obj.GetValue()
        mean_val = self.offset_mean(val, index)
        self.update_graph(mean_val, index)
        print(self.axes1)
        self.move_line(val)
        print(str(val))
        print(mean_val)

    def move_line(self, val):
        x, y = self.figure_canvas.line.get_data()

        x = [val] * self.HEIGHT
        self.figure_canvas.line.set_xdata(np.array(x) + 0.001)
        # self.axes1.set_xbound([0, x[-1] + 1])
        self.figure_canvas.draw()

    def offset_mean(self, val, col_num):
        """
        Determine mean value of col_num column between val to end of the array
        """
        col = self.Data.Data[:, col_num]
        fudge_factor = len(col) / float(self.datapanel.SLIDER_MAX)
        # print(col)
        return np.min(col[int(fudge_factor) * val:])

    def update_graph(self, mean_val, col_num):
        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']
        data = np.copy(self.Data.Data)
        data[:, col_num] = self.Data.Data[:, col_num] - mean_val
        for i, label, colour in zip(data[:, 1:].T, labels, colours):

            self.axes1.plot(
                data[::1, 0],
                i[::1],
                '.',
                color=colour,
                # Label=label
            )
        del self.axes1.lines[1:4]
