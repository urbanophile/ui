import wx

from gui.view1 import View1
from hardware.MeasurementHandler import MeasurementHandler

from models.ExperimentSettings import ExperimentSettings
from models.LightPulse import LightPulse
from models.PCCalibrationData import PCCalibrationData
from models.TemperatureSettings import TemperatureSettings
from models.Wafer import Wafer

from util.utils import load_metadata, save_metadata


class Controller(object):
    """docstring for Controller"""
    def __init__(self, app, view1):
        super(Controller, self).__init__()
        self.view1 = view1

        self.data_dir = None
        self._set_event_bindings()
        self.view1.Show()

        # app state
        self.uploaded = False

        # the hardware interface
        self.measurement_handler = MeasurementHandler()

        # settings
        self.temperature_settings = None
        self.wafer_settings = None
        # data sets
        self.pc_calibration_data = PCCalibrationData()

    def data_output_dir(self, event):
        self.data_dir = self.view1.ask_user_for_dir()

    def save_settings(self, event):
        settings = {}
        settings["temperature_settings"] = self.view1.get_temperature_form()
        settings["experiment_settings"] = self.view1.get_experiment_form()

        file_dir, file_name = self.view1.askUserForFilename(
            style=wx.SAVE,
            **self.view1.default_file_dialog_options()
        )
        if file_dir is not None:
            # utils.save_data(self.Data.Data, self.data_file, self.dirname)
            save_metadata(settings, file_name, file_dir)

    def load_settings(self, event):
        print("load_settings")

        self.view1.clear_experiment_form()

        self.measurement_handler.clear_queue()
        file_dir, file_name = self.view1.askUserForFilename(
            style=wx.OPEN,
            **self.view1.default_file_dialog_options()
        )
        if file_dir is not None:
            # try:
            config_dict = load_metadata(file_name, file_dir)
            settings = self._parse_config(config_dict)
            for setting in settings["experiment_settings"]:
                self.measurement_handler.add_to_queue(
                    LightPulse(setting).create_waveform(),
                    setting
                )
            self.temperature_settings = settings["temp_settings"]
            # except Exception as e:
            #     print("an Exception occured:{0}".format(e))
        self.view1.set_experiment_form(
            self.measurement_handler.as_list()
        )
        print(self.measurement_handler.as_list())

        self.view1.set_temperature_form(
            self.temperature_settings.as_dict()
        )

    def upload(self, event):
        self.measurement_handler.clear_queue()
        file_dir, file_name = self.view1.askUserForFilename(
            style=wx.OPEN,
            **self.view1.default_file_dialog_options()
        )
        if file_dir is not None:
            config_dict = load_metadata(file_name, file_dir)
            settings = self._parse_config(config_dict)
            for setting in settings["experiment_settings"]:
                self.measurement_handler.add_to_queue(
                    LightPulse(setting).create_waveform(),
                    setting
                )

            self.temperature_settings = settings["temp_settings"]

            self.view1.set_temperature_form(
                self.temperature_settings.as_dict()
            )
            self.view1.disable_all_settings_inputs()
            self.view1.show_info_modal(
                "{0} experiment settings uploaded successfully!".format(
                    len(self.measurement_handler._queue)
                )
            )
            self.uploaded = True

    def display(self, event):
        pass

    def perform_measurement(self, event):
        # first save wafer settings to disk
        if self.data_dir is not None:
            save_metadata(
                self.wafer_settings.as_dict,
                self.wafer_settings.id,
                self.data_dir
            )

        if not self.uploaded:
            config_dict = {}
            config_dict["temperature_settings"] = (
                self.view1.get_temperature_form()
            )
            config_dict["wafer_settings"] = self.view1.get_wafer_form()
            config_dict["experiment_settings"] = (
                self.view1.get_experiment_form()
            )
            settings = self._parse_config(config_dict)
            for setting in settings["experiment_settings"]:
                self.measurement_handler.add_to_queue(
                    LightPulse(setting).create_waveform(),
                    setting
                )
            self.wafer_settings = settings["wafer_settings"]
            self.temperature_settings = settings["temp_settings"]

        self.measurement_handler.series_measurement(
            self.data_dir,
            self.wafer_settings.id
        )

    def calibrate_pc(self, event):
        self.view1.show_calibration_modal()

        null_metadata = ExperimentSettings()
        null_metadata.waveform = "NullWave"

        pc_data = self.measurement_handler.pc_calibration_measurement(
            null_metadata
        )

        self.pc_calibration.update_data(pc_data)

    def show_calibration_const(self, event):
        message = str(self.pc_calibration_data.as_dict())
        self.view1.show_info_modal(message)

    def _set_event_bindings(self):

        self.view1.m_dataOutputDir.Bind(wx.EVT_BUTTON, self.data_output_dir)
        self.view1.m_save.Bind(wx.EVT_BUTTON, self.save_settings)
        self.view1.m_load.Bind(wx.EVT_BUTTON, self.load_settings)
        self.view1.m_upload.Bind(wx.EVT_BUTTON, self.upload)
        self.view1.m_display.Bind(wx.EVT_BUTTON, self.display)
        self.view1.m_performMeasurement.Bind(
            wx.EVT_BUTTON, self.perform_measurement
        )
        self.view1.m_calibratePC.Bind(
            wx.EVT_BUTTON, self.calibrate_pc
        )
        self.view1.m_showCalibrationConst.Bind(
            wx.EVT_BUTTON, self.show_calibration_const
        )

    def _parse_config(self, config):
        settings = {}
        measurement_list = []
        experiments_list = config["experiment_settings"]
        for item in experiments_list:
            measurement_list.append(
                ExperimentSettings(
                    waveform=item['waveform'],
                    duration=item['duration'],
                    amplitude=item['amplitude'],
                    offset_before=item['offset_before'],
                    offset_after=item['offset_after'],
                    sample_rate=item['sample_rate'],
                    channel=item['channel'],
                    binning=item['binning'],
                    averaging=item['averaging']
                )
            )
        settings["experiment_settings"] = measurement_list
        settings["temp_settings"] = TemperatureSettings(
            start_temp=config["temperature_settings"]["start_temp"],
            end_temp=config["temperature_settings"]["end_temp"],
            step_temp=config["temperature_settings"]["step_temp"]
        )
        try:
            settings["wafer_settings"] = Wafer(
                wafer_id=config["wafer_settings"]["wafer_id"],
                thickness=config["wafer_settings"]["wafer_thickness"],
                codoped=config["wafer_settings"]["wafer_codoped"],
                na=config["wafer_settings"]["wafer_na"],
                nd=config["wafer_settings"]["wafer_nd"],
                diffused=config["wafer_settings"]["wafer_diffused"],
                num_sides=config["wafer_settings"]["wafer_num_sides"]
            )
        except Exception as e:
            print("problems with wafer settings: {0}".format(e))
        return settings

if __name__ == "__main__":
    app = wx.App(False)
    view1 = View1(None)
    controller = Controller(app, view1)
    app.MainLoop()
