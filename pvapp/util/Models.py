# for data models
import scipy
import numpy as np
import scipy.fftpack
from util import utils
from util.Constants import (
    CHANNEL_INDEX,
    LOW_VOLTAGE_LIMIT,
    HIGH_VOLTAGE_LIMIT,
    THRESHOLD_CONST,
    HIGH_HARDWARE_CONST,
    LOW_HARDWARE_CONST,
    MAX_INPUT_SAMPLE_RATE,
)

# TODO: Remove when testing complete
from test.utils import make_sin_data


class PCCalibrationData(object):

    def __init__(self):
        self.calibration_mean = None
        self.calibration_std = None

    def update_data(self, data):
            self.pc_calibration_mean = np.mean(data[:, CHANNEL_INDEX['PC']])
            self.pc_calibration_std = np.std(data[:, CHANNEL_INDEX['PC']])


class ExperimentSettings(object):
    """docstring for ExperimentSettings"""

    def __init__(self, waveform='Sin', duration=1, amplitude=0.5,
                 offset_before=1, offset_after=10, sample_rate=1.2e3,
                 channel=r'High (2A/V)', binning=1, averaging=1):

        self.waveform = waveform

        self.duration = duration  # seconds, a.k.a. period
        self._amplitude = amplitude  # amps

        self.offset_before = offset_before  # seconds
        self.offset_after = offset_after  # seconds

        self.sample_rate = sample_rate
        self.channel = channel

        self.binning = binning
        self.averaging = averaging

        # what follows are hardward settings
        self.threshold = 150.0

        self.output_sample_rate = 1.2e3

        self.inverted_channels = {
            'Reference': False,
            'PC': False,
            'PL': True
        }
        self.input_voltage_range = 10.0
        self.output_voltage_range = 10.0  # volts

        self._voltage_threshold = 150.0
        self.channel_name = None

        self.pc_calibration = PCCalibrationData()

        self._determine_output_channel()

    def _determine_output_channel(self):
        # Just a simple function choosing the correct output channel
        # based on the drop down box
        if self.channel == 'High (2A/V)':
            self.channel_name = r'ao0'
            self.voltage_threshold = self.threshold / HIGH_HARDWARE_CONST
        elif self.channel == r'Low (50mA/V)':
            self.channel_name = r'ao1'
            self.voltage_threshold = self.threshold / LOW_HARDWARE_CONST

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amp):
        """
        Determines the appropriate current limit for the box
        """
        if self.channel == r'Low (50mA/V)' and amp > LOW_VOLTAGE_LIMIT:
            self._amplitude = LOW_VOLTAGE_LIMIT
        elif self.channel == r'High (2A/V)' and amp > HIGH_VOLTAGE_LIMIT:
            self._amplitude = HIGH_VOLTAGE_LIMIT
        else:
            self._amplitude = amp

    @property
    def voltage_threshold(self):
        return self._voltage_threshold

    @voltage_threshold.setter
    def voltage_threshold(self, v_threshold):
        if v_threshold > self.amplitude:
            if v_threshold > LOW_HARDWARE_CONST * THRESHOLD_CONST:
                self._voltage_threshold = LOW_HARDWARE_CONST * THRESHOLD_CONST
            else:
                self._voltage_threshold = v_threshold
        else:
            self._voltage_threshold = v_threshold

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, s_rate):
        if s_rate > MAX_INPUT_SAMPLE_RATE:
            self._sample_rate = MAX_INPUT_SAMPLE_RATE
        else:
            self._sample_rate = s_rate

    def get_settings_as_dict(self):
        meta_data = {
            'channel': self.channel,
            'averaging': self.averaging,
            'measurement_binning': self.binning,
            'threshold_mA': self.threshold,
            'inverted_channels': self.inverted_channels,

            'sample_rate': self.sample_rate,
            'output_sample_rate': self.output_sample_rate,

            "input_voltage_range": self.input_voltage_range,
            "output_voltage_range": self.output_voltage_range,
            "waveform": self.waveform,
            "amplitude": self.amplitude,

            "offset_before": self.offset_before,
            "offset_after": self.offset_after,
            "duration": self.duration,
            "voltage_threshold": self.voltage_threshold,
            "channel_name": self.channel_name,

            "pc_calibration_mean": self.pc_calibration.calibration_mean,
            "pc_calibration_std": self.pc_calibration.calibration_std
        }
        return meta_data

    def get_total_time(self):
        return sum([self.offset_before / 1000, self.offset_after / 1000,
                    self.duration])

    def get_frequency(self):
        return 1 / self.duration

    def get_total_data_points(self):
        return (self.get_total_time() * self.sample_rate / self.binning)


class ExperimentData(object):
    """docstring for ExperimentData"""
    def __init__(self, data=None, metadata=None):
        super(ExperimentData, self).__init__()

        # make secondary dataset
        data = make_sin_data(duration=100)

        self.Data = data
        self.RawData = data
        self.metadata = metadata

    ####################################
    # Data Transformation Event Handlers
    #

    def isDataEmpty(self):
        return self.Data is None

    def updateRawData(self, data):
        self.Data = data
        self.RawData = np.copy(data)

    def revertData(self):
        self.Data = np.copy(self.RawData)

    def invertHandler(self, channel):
        self.Data[:, CHANNEL_INDEX[channel]] *= -1
        self.metadata.inverted_channels[channel] = not self.metadata.inverted_channels[channel]

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

    def fftOperator(self, channel_name, total_duration):
        # get FFT of data
        # pass FFT of data to plotting function
        # frequency spectrum data
        t = scipy.linspace(0, total_duration, self.metadata.sample_rate)

        signal = self.Data[:, CHANNEL_INDEX[channel_name]]
        FFT = abs(scipy.fft(signal))

        # returns DFT sample frequencies
        freqs = scipy.fftpack.fftfreq(
            signal.size,  # window length
            t[1] - t[0]  # sample spacing
        )
        pos_freqs = freqs[freqs >= 0]
        FFT_transf = FFT[len(pos_freqs) - 1:]
        # print(pos_freqs.size, FFT_transf.size)
        return np.vstack((pos_freqs, FFT_transf)).T

    def binHandler(self, bin_size):
        self.Data = utils.bin_data(self.Data, bin_size)
