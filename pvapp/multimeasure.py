import wx
import os

from gui.new_gui import IncrementalApp
from gui.Validator import NumRangeValidator

from util.Models import ExperimentSettings
from util.utils import load_metadata, save_metadata
from hardware.daq import LightPulse
from hardware.MeasurementHandler import MeasurementHandler
from util.Constants import WAVEFORMS, OUTPUTS


class View1(IncrementalApp):
    def __init__(self, parent):
        IncrementalApp.__init__(self, parent)

        self.dirname = os.getcwd()
        self.data_file = None

        # hardware layout
        self._pl_calibration_labels = [
            "Self-consistent",
            "Nan's method",
            "Other",
            "None"
        ]
        self._yes_no_labels = [
            "Yes",
            "No"
        ]

        self._num_sides_labels = [
            "1 side",
            "2 sides"
        ]
        self._set_hardware_dropdowns()

        # experiment settings layout
        self.input_rows = []
        column_titles_str = [
            u"", u"Waveform", u"Period", u"Amplitude", u"Offset1",
            u"Offset2", u"Sample Rate", u"LED state", u"Filter", u"Binning"
        ]

        # setup flexible grid sizer for form construction
        self.fgSizerAuto = wx.FlexGridSizer(5, 10, 0, 0)
        self.fgSizerAuto.SetFlexibleDirection(wx.BOTH)
        self.fgSizerAuto.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        for title in column_titles_str:
            self._add_title_row(title)

        for num in range(1, 5):
            self.input_rows.append(self._add_row(num))

        self.m_autoPanel.SetSizer(self.fgSizerAuto)
        self.m_autoPanel.Layout()
        # self.fgSizerAuto.Fit(self.m_autoPanel)

        self.Layout()

        self._set_ui_validators()
        self._bind_checkbox_disable()

    def get_ui_input_temperature(self):
        return (
            int(self.m_startTemp.GetValue()),
            int(self.m_endTemp.GetValue()),
            int(self.m_stepTemp.GetValue())
        )

    def get_ui_input_settings(self):
        inputs = []
        for row in self.input_rows:
            row_inputs = []
            for entry in row:
                if isinstance(entry, wx.Choice):
                    row_inputs.append(entry.GetSelection())
                else:
                    row_inputs.append(entry.GetValue())
            inputs.append(row_inputs)
        return inputs

    def set_ui_input_temperature(self):
        pass

    def set_ui_input_settings(self):
        pass

    def disable_all_settings_inputs(self):
        for row in self.input_rows:
            self._disable_row(row)

    def _bind_checkbox_disable(self):
        for row in self.input_rows:
            row[0].Bind(
                wx.EVT_CHECKBOX,
                self._disable_part_row
            )

    def _disable_part_row(self, event):
        sender = event.GetEventObject()

        checkbox_list = [row[0] for row in self.input_rows]
        row_num = checkbox_list.index(sender)

        isChecked = sender.GetValue()

        if isChecked:
            self._enable_row(self.input_rows[row_num], start_element=1)
        else:
            self._disable_row(self.input_rows[row_num], start_element=1)

    def _disable_row(self, row, start_element=0):
        for index, element in enumerate(row):
            if index >= start_element:
                element.Disable()

    def _enable_row(self, row, start_element=0):
        for index, element in enumerate(row):
            if index >= start_element:
                element.Enable()

    def _set_hardware_dropdowns(self):
        self.m_plCalibrationMethod.SetItems(self._pl_calibration_labels)
        self.m_waferCodoped.SetItems(self._yes_no_labels)
        self.m_waferDiffused.SetItems(self._yes_no_labels)
        self.m_waferNumSides.SetItems(self._num_sides_labels)

    def _add_row(self, number):
        row_elements = []
        row_elements.append(self._add_checkbox(unicode(number)))
        row_elements.append(self._add_dropdown(WAVEFORMS))
        for i in range(5):
            row_elements.append(self._add_textctrl())
        row_elements.append(self._add_dropdown(OUTPUTS))
        for i in range(2):
            row_elements.append(self._add_textctrl())
        return row_elements

    def _add_title_row(self, row_title):
        row = wx.StaticText(
            self.m_autoPanel, wx.ID_ANY, row_title,
            wx.DefaultPosition, wx.DefaultSize, 0
        )
        row.Wrap(-1)
        self.fgSizerAuto.Add(row, 0, wx.ALL, 5)
        return row

    def _add_checkbox(self, number):
        checkbox = wx.CheckBox(
            self.m_autoPanel, wx.ID_ANY, number, wx.DefaultPosition,
            wx.DefaultSize, 0
        )
        checkbox.SetValue(True)
        self.fgSizerAuto.Add(checkbox, 0, wx.ALL, 5)
        return checkbox

    def _add_textctrl(self):
        text_ctrl = wx.TextCtrl(
            self.m_autoPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, 0
        )
        text_ctrl.SetMaxSize(wx.Size(50, -1))
        self.fgSizerAuto.Add(text_ctrl, 0, wx.ALL, 5)
        return text_ctrl

    def _add_dropdown(self, options):
        dropdown = wx.Choice(
            self.m_autoPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            options, 0
        )
        dropdown.SetSelection(0)
        self.fgSizerAuto.Add(dropdown, 0, wx.ALL, 5)
        return dropdown

    def _set_ui_validators(self):
        self.m_startTemp.SetValidator(NumRangeValidator(numeric_type='int'))
        self.m_endTemp.SetValidator(NumRangeValidator(numeric_type='int'))
        self.m_stepTemp.SetValidator(NumRangeValidator(numeric_type='int'))

    def default_file_dialog_options(self):
        """
        Return a dictionary with file dialog options that can be
        used in both the save file dialog as well as in the open
        file dialog.
        """
        return dict(
            message='Choose a file',
            defaultDir=self.dirname,
            wildcard='*.*'
        )

    def askUserForFilename(self, **dialogOptions):
        dialog = wx.FileDialog(self, **dialogOptions)
        path_parameters = None, None
        if dialog.ShowModal() == wx.ID_OK:
            path_parameters = dialog.GetFilename(), dialog.GetDirectory()
        dialog.Destroy()
        return path_parameters


class Controller(object):
    """docstring for Controller"""
    def __init__(self, app):
        super(Controller, self).__init__()
        self.view1 = View1(None)

        self.data_dir = None
        self._set_event_bindings()
        self.view1.Show()

        self.measurement_handler = MeasurementHandler()

    def data_output_dir(self, event):

        print("save data dir")
        self.data_dir, file_name = self.view1.askUserForFilename(
            style=wx.SAVE,
            **self.view1.default_file_dialog_options()
        )

    def save_settings(self, event):

        print(self.view1.get_ui_input_settings())
        print(self.view1.get_ui_input_temperature())

        print("on save_settings")
        if self.view1.askUserForFilename(
            style=wx.SAVE,
            **self.view1.default_file_dialog_options()
        ):
            # utils.save_data(self.Data.Data, self.data_file, self.dirname)
            save_metadata(
                self.measurement_handler.settings_as_list()
            )

    def load_settings(self, event):
        print("on load_settings")
        file_dir, file_name = self.view1.askUserForFilename(
            style=wx.OPEN,
            **self.view1.default_file_dialog_options()
        )
        if file_dir is not None:
            try:
                config_dict = load_metadata(file_name, file_dir)
                settings_list = self._parse_config(config_dict)
                for setting in settings_list:
                    self.measurement_handler.add_to_queue(
                        LightPulse(setting).create_waveform(),
                        setting
                    )
            except Exception:
                pass
        self.view1.set_ui_input_settings(
            self.measurement_handler.settings_as_list()
        )

    def upload(self, event):
        print("on hard_mode")
        file_name, file_dir = self.view1.askUserForFilename(
            style=wx.OPEN,
            **self.view1.default_file_dialog_options()
        )

        if file_dir is not None:
            try:
                config_dict = load_metadata(file_name, file_dir)
                settings_list = self._parse_config(config_dict)
                for setting in settings_list:
                    self.measurement_handler.add_to_queue(
                        LightPulse(setting).create_waveform(),
                        setting
                    )
                self.view1.disable_all_settings_inputs()
            except Exception:
                pass

    def display(self, event):
        pass

    def perform_measurement(self, event):
        pass

    def _set_event_bindings(self):

        self.view1.m_dataOutputDir.Bind(wx.EVT_BUTTON, self.data_output_dir)
        self.view1.m_save.Bind(wx.EVT_BUTTON, self.save_settings)
        self.view1.m_load.Bind(wx.EVT_BUTTON, self.load_settings)
        self.view1.m_upload.Bind(wx.EVT_BUTTON, self.upload)
        self.view1.m_display.Bind(wx.EVT_BUTTON, self.display)
        self.view1.m_performMeasurement.Bind(wx.EVT_BUTTON,
                                             self.perform_measurement)

    def _parse_config(self, config):
        measurement_list = []
        for item in config:
            self.measurement_list.append(
                ExperimentSettings(
                    waveform=config['waveform'],
                    duration=config['duration'],
                    amplitude=config['amplitude'],
                    offset_before=config['offset_before'],
                    offset_after=config['offset_after'],
                    sample_rate=config['sample_rate'],
                    channel=config['channel'],
                    binning=config['binning'],
                    averaging=config['averaging']
                )
            )
        return measurement_list

if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    app.MainLoop()
