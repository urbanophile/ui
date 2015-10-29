import wx

from gui.view1 import View1

from util.Models import ExperimentSettings
from util.utils import load_metadata, save_metadata
from hardware.daq import LightPulse
from hardware.MeasurementHandler import MeasurementHandler


class Controller(object):
    """docstring for Controller"""
    def __init__(self, app, view1):
        super(Controller, self).__init__()
        self.view1 = view1

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
    view1 = View1(None)
    controller = Controller(app, view1)
    app.MainLoop()
