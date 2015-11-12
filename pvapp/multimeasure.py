import wx
import os
import time

from gui.view1 import View1
from gui.PlotModal import PlotModal
from hardware.MeasurementHandler import MeasurementHandler

from models.ExperimentSettings import ExperimentSettings
from models.LightPulse import LightPulse
from models.PCCalibrationData import PCCalibrationData
from models.TemperatureSettings import TemperatureSettings
from models.Wafer import Wafer

from util.utils import load_metadata, save_metadata
from util.utils import save_data
from util.Exceptions import PVInputError


class Controller(object):
    """A Controller to coordinate the UI, data, and hardware"""

    def __init__(self, app, view1):
        """
        :params app: a wx App object
        :params view1: a wx Frame object
        """
        super(Controller, self).__init__()
        self.view1 = view1
        self.app = app

        # make directory for storing data files
        self.app_dir = os.getcwd()
        data_dir = os.path.join(self.app_dir, "data_directory")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_dir = data_dir

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
        """
        Select a different directory to save experimental results
        """

        self.data_dir = self.view1.ask_user_for_dir(
            message="Choose a directory",
            defaultPath=self.data_dir,
        )

    def save_settings(self, event):
        """
        Saves settings as displayed in the forms
        """
        settings = {}
        settings["temperature_settings"] = self.view1.get_temperature_form(
            allow_incomplete=True
        )
        settings["experiment_settings"] = self.view1.get_experiment_form(
            allow_incomplete=True
        )

        file_dir, file_name = self.view1.ask_user_for_filename(
            defaultDir=self.app_dir,
            message='Save your file',
            wildcard='*.*',
            style=wx.SAVE
        )
        if file_dir is not None:
            save_metadata(settings, file_name, file_dir)

    def load_settings(self, event):
        """
        Loads settings from the forms
        """
        # TODO: change so just fills form out
        # and then reads into data structure when press perform measurement

        self.view1.clear_experiment_form()

        self.measurement_handler.clear_queue()
        file_dir, file_name = self.view1.ask_user_for_filename(
            defaultDir=self.app_dir,
            message='Choose a file',
            wildcard='*.*',
            style=wx.OPEN
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
            #     print("An Exception occurred: {0}".format(e))
        self.view1.set_experiment_form(
            self.measurement_handler.as_list()
        )

        self.view1.set_temperature_form(
            self.temperature_settings.as_dict()
        )
        self.measurement_handler.clear_queue()

    def upload(self, event):
        """
        Bulk upload settings from a text file
        """
        self.measurement_handler.clear_queue()
        file_dir, file_name = self.view1.ask_user_for_filename(
            defaultDir=self.app_dir,
            style=wx.OPEN,
            message='Choose a file',
            wildcard='*.*'
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
        """
        Plot waveforms in modal
        """
        self.PlotModal = PlotModal(self.app)

        waveform_list = []
        settings_dict = {}

        try:
            settings_dict["experiment_settings"] = self.view1.get_experiment_form()
            experiment_settings = self._parse_experiment_settings(settings_dict)
            for setting in experiment_settings:
                waveform_list.append(-LightPulse(setting).create_waveform())

            self.PlotModal.Show()
            self.PlotModal.plot_data(waveform_list)
        except PVInputError as e:
            self.view1.show_error_modal(str(e))

    def perform_measurement(self, event):
        """
        Perform the queued measurements
        """

        try:
            if not self.uploaded:
                # try to retrieve settings from the various forms
                config_dict = {}
                config_dict["temperature_settings"] = (
                    self.view1.get_temperature_form()
                )
                config_dict["wafer_settings"] = self.view1.get_wafer_form()
                config_dict["experiment_settings"] = (
                    self.view1.get_experiment_form()
                )
                try:
                    settings = self._parse_config(config_dict)
                except KeyError as e:
                    self.view1.show_error_modal(str(e))

                for setting in settings["experiment_settings"]:
                    self.measurement_handler.add_to_queue(
                        LightPulse(setting).create_waveform(),
                        setting
                    )
                self.wafer_settings = settings["wafer_settings"]
                self.temperature_settings = settings["temp_settings"]

            if self.data_dir is not None:
                save_metadata(
                    self.wafer_settings.as_dict(),
                    self.data_dir,
                    self.wafer_settings.id
                )

            if self.measurement_handler.is_queue_empty():
                raise(PVInputError("No measurements loaded."))

            # Do the actual measurements
            # TODO: refactor in separate method

            dataset_list = []
            total_measurements = 0
            self.PlotModal = PlotModal(self.app)
            self.PlotModal.Show()
            while not self.measurement_handler.is_queue_empty():

                single_dataset = self.measurement_handler.single_measurement()
                dataset_list.append(single_dataset)
                total_measurements = total_measurements + 1
                ts = int(time.time())
                dataset_name = (
                    str(total_measurements) +
                    self.wafer_settings.id +
                    str(ts)
                )
                save_data(single_dataset, dataset_name, self.data_dir)

                # print single_dataset.shape
                self.PlotModal.plot_data([x for x in single_dataset[:,1:].T])

        except PVInputError as e:
            self.view1.show_error_modal(str(e))

    def calibrate_pc(self, event):
        """"
        Perform and calibrate the PC measurement
        """
        self.view1.show_calibration_modal()

        null_metadata = ExperimentSettings()
        null_metadata.waveform = "NullWave"

        pc_data = self.measurement_handler.pc_calibration_measurement(
            null_metadata
        )

        self.pc_calibration.update_data(pc_data)

    def show_calibration_const(self, event):
        """
        Display the calibration constants
        """
        message = str(self.pc_calibration_data.as_dict())
        self.view1.show_info_modal(message)

    def _set_event_bindings(self):
        """
        Setups all program behavior which isn't strictly related to the UI
        """

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

    def _parse_experiment_settings(self, config):
        measurement_list = []
        experiments_list = config["experiment_settings"]
        for item in experiments_list:
            try:
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
            except KeyError as e:
                raise("Missing value in Experiment Settings: {0}".format(e))

        return measurement_list

    def _parse_config(self, config):
        """
        Takes a dictionary of settings and constructs appropriate objects
        """

        settings = {}
        settings["experiment_settings"] = self._parse_experiment_settings(
            config
        )

        try:
            settings["temp_settings"] = TemperatureSettings(
                start_temp=config["temperature_settings"]["start_temp"],
                end_temp=config["temperature_settings"]["end_temp"],
                step_temp=config["temperature_settings"]["step_temp"],
                step_wait=config["temperature_settings"]["step_wait"],
                temperature_scale=config["temperature_settings"][
                    "temperature_scale"
                ]
            )
        except KeyError as e:
            raise KeyError(
                "Missing value in Temperature Settings: {0}".format(e)
            )
        try:
            settings["wafer_settings"] = Wafer(
                wafer_id=config["wafer_settings"]["wafer_id"],
                thickness=config["wafer_settings"]["wafer_thickness"],
                na=config["wafer_settings"]["wafer_na"],
                nd=config["wafer_settings"]["wafer_nd"],
                diffused=config["wafer_settings"]["wafer_diffused"],
                num_sides=config["wafer_settings"]["wafer_num_sides"]
            )
        except KeyError as e:
            raise KeyError("Missing value in Wafer settings: {0}".format(e))
        return settings

if __name__ == "__main__":
    app = wx.App(False)
    view1 = View1(None)
    controller = Controller(app, view1)
    app.MainLoop()
