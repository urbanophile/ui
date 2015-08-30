# for data models
import scipy
import numpy as np
import scipy.fftpack

from util import utils
from hardware import daq


# TODO: Remove when testing complete
from test.utils import make_sin_data
from util.Constants import (
    CHANNEL_INDEX,
    LOW_VOLTAGE_LIMIT,
    HIGH_VOLTAGE_LIMIT,
    THRESHOLD_CONST,
    HIGH_HARDWARE_CONST,
    LOW_HARDWARE_CONST
)
# Magic numbers relating to hardware. They convert sent voltage to current.
# They are determined by experimental measurement


class ExperimentSettings(object):
    """docstring for ExperimentSettings"""

    def __init__(self):
        # super(ExperimentSettings, self).__init__()
        self.binning = 1
        self.averaging = 1
        self.channel = r'Low (50mA/V)'
        self.threshold = 150.0

        self.inverted_channels = {
            'Reference': False,
            'PC': False,
            'PL': True
        }
        self.sample_rate = float(np.float32(daq.DAQmx_InputSampleRate))
        self.InputVoltageRange = 10.0

        self.waveform = 'Cos'
        self.amplitude = 0.5
        self.offset_before = 1
        self.offset_after = 10
        self.duration = 1

        self.voltage_threshold = 150.0
        self.channel_name = None

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
