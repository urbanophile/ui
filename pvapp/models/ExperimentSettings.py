from PCCalibrationData import PCCalibrationData
from util.Constants import (
    OUTPUTS,
    LOW_VOLTAGE_LIMIT,
    HIGH_VOLTAGE_LIMIT,
    THRESHOLD_CONST,
    HIGH_HARDWARE_CONST,
    LOW_HARDWARE_CONST,
    MAX_INPUT_SAMPLE_RATE,
)


class ExperimentSettings(object):
    """docstring for ExperimentSettings"""

    def __init__(self, waveform='Sin', duration=1, amplitude=0.5,
                 offset_before=1, offset_after=10, sample_rate=1.2e3,
                 channel=1, binning=1, averaging=1):

        self.waveform = waveform

        self.duration = duration  # seconds, a.k.a. period
        self._amplitude = amplitude  # amps

        self.offset_before = offset_before  # seconds
        self.offset_after = offset_after  # seconds

        self.sample_rate = sample_rate
        self.channel = OUTPUTS[channel]

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

    def as_dict(self):
        return {
            "waveform": self.waveform,
            "duration": self.duration,
            "amplitude": self._amplitude,

            "offset_before": self.offset_before,
            "offset_after": self.offset_after,
            "sample_rate": self.sample_rate,
            # ensures dict is passed to view in comprehensible format
            "channel": OUTPUTS.index(self.channel),

            "binning": self.binning,
            "averaging": self.averaging
        }

    def get_total_time(self):
        return sum([self.offset_before / 1000, self.offset_after / 1000,
                    self.duration])

    def get_frequency(self):
        return 1 / self.duration

    def get_total_data_points(self):
        return (self.get_total_time() * self.sample_rate / self.binning)
