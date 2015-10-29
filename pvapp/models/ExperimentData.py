import numpy as np
import scipy

from util.Constants import (
    CHANNEL_INDEX,
)

from test.utils import make_sin_data


class ExperimentData(object):
    """docstring for ExperimentData"""
    def __init__(self, data=None, metadata=None):
        super(ExperimentData, self).__init__()

        # make secondary dataset
        data = make_sin_data(duration=100)

        self.Data = data
        self.RawData = data
        self.metadata = metadata

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
