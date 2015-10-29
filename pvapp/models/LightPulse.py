import numpy as np
from scipy import signal
from util.Constants import WAVEFORMS


class LightPulse(object):
    """
    Represents different wave forms to be sent to play
    """

    def __init__(self, metadata):

        assert metadata.duration > 0
        assert metadata.offset_after >= 0
        assert metadata.offset_before >= 0
        assert metadata.amplitude > 0
        assert metadata.sample_rate > 0

        self.Waveform = WAVEFORMS[metadata.waveform]
        self.A = metadata.amplitude
        self.Offset_Before = metadata.offset_before
        self.Offset_After = metadata.offset_after
        self.Duration = metadata.duration
        self.output_samples = np.float32(metadata.sample_rate)
        self.Voltage_Threshold = metadata.voltage_threshold
        self.time_array = np.array([])

        self.complete_waveform = self.create_waveform()

        self._set_derived_parameters()

    def __repr__(self):
        description = (
            "<LightPulse object: {0}, {1} A, {2} Time, {3} V Threshold>"
        ).format(
            self.Waveform,
            self.A,
            self.Duration,
            self.Voltage_Threshold
        )
        return description

    def _set_derived_parameters(self):
        self.total_time = (
            self.Duration + self.Offset_Before / 1000 + self.Offset_After / 1000
        )
        self.frequence_val = 1. / self.total_time

    # TODO: should be private method
    def create_waveform(self):
        """
        Factory method to produce numpy array with light intensity values
        """
        # pad waveform with zeroes

        v_before = np.zeros(
            int(self.output_samples * self.Offset_Before / 1000)
        )
        v_after = np.zeros(
            int(self.output_samples * self.Offset_After / 1000)
        )

        if self.Waveform == 'FrequencyScan':
            # TODO: this is bad refactor
            result = self.FrequencyScan(self.Duration)
            voltage_waveform, self.time_array = result[0], result[1]
            voltage_waveform -= self.Voltage_Threshold

        else:
            self.time_array = np.linspace(
                0, self.Duration, num=(self.output_samples * self.Duration)
            )

            # TODO: this is bad, refactor
            voltage_waveform = getattr(self, self.Waveform)(
                self.time_array, self.A
            )
            voltage_waveform = self.scale_to_threshold(voltage_waveform)

        self.Duration = self.time_array[-1]
        # print (v_before, v_after)
        complete_waveform = np.concatenate(
            (v_before, voltage_waveform, v_after)
        )

        total_time = sum([self.Offset_Before / 1000,
                          self.Offset_After / 1000,
                          self.Duration])
        self.time_array = np.linspace(
            0, total_time, num=complete_waveform.shape[0]
        )
        return complete_waveform

    # TODO: also should be Private method
    def scale_to_threshold(self, voltage_waveform):
        """
        Scales an array of voltage values to below voltage_threshold
        """
        #  everything is reversed because amplitude is negative
        max_voltage = np.amax(abs(voltage_waveform))
        if np.abs(max_voltage) > 0:
            scale_factor = (max_voltage - self.Voltage_Threshold) / max_voltage
            voltage_waveform *= scale_factor
        voltage_waveform -= self.Voltage_Threshold
        return voltage_waveform

    def Sin(self, time_array, amplitude):
        """
        Returns t sized array with values of sine wave over half the period
        """
        return -(amplitude) * np.abs(np.sin(np.pi * time_array / time_array[-1]))

    def Square(self, time_array, amplitude):
        """
        Returns t sized array with values -A
        """
        return -amplitude * np.ones((time_array.shape[0]))

    def Cos(self, time_array, amplitude):
        """
        Returns t sized array with equally spaced values sampled from
        0.5 * (cos(t) + A) over period 0 to pi
        """
        scale_factor = amplitude * 0.5
        cos_values = np.cos(np.pi * time_array / time_array[-1])
        return - scale_factor * cos_values - scale_factor

    # BUG: something is funny with the implementation doesn't
    def Triangle(self, time_array, amplitude, width=0.5):
        """
        Returns t sized array of equally spaced points from triangle wave
        with peak at t/2. See details in underlying scipy.signal.sawtooth
        """
        t_length = time_array.shape[0]
        wave = signal.sawtooth(2 * np.pi * np.linspace(0, 1, t_length), 0.5)
        return -amplitude * 0.5 * (wave + 1)

    def NullWave(self, time_array, amplitude):
        """
        Returns t sized array with values -A
        """
        return np.zeros((time_array.shape[0]))

    # TODO: rename to more  descriptive
    def MattiasCustom(self, time_array, amplitude):
        """
        Return t sized array evenly space points on 1/x on log scale
        """
        fraction = 0.01
        t_shift = time_array.shape[0] * fraction
        t0_index = time_array.shape[0] * (0.5 - fraction)
        midpoint = time_array.shape[0] / 2
        t_halfway = time_array[midpoint]

        # Functions are:
        # G = C/t
        # G = Bx^4 + Amplitude
        # These are then spliced together at t0

        B = -self.A * time_array[t_shift] ** (-4) / 5.
        C = 4. / 5 * self.A * time_array[t_shift]
        f = np.concatenate((
            -C / (time_array[:t0_index] - t_halfway),
            B * (time_array[t0_index:midpoint] - t_halfway) ** 4 + amplitude
        ))
        return -1 * np.concatenate((f, f[::-1]))

    def FrequencyScan(self, number):
        """
        Another custom Mattias function
        """
        Amplitudefreaction = 0.025
        Inital_Time_Delay = 0.01

        V = np.zeros(self.output_samples * .1)
        T = np.linspace(0, Inital_Time_Delay, self.output_samples * .1)
        t0 = T[-1]

        for f in np.logspace(self.Offset_Before, self.Offset_After, int(number))[::-1]:

            t = np.arange(0, 10 / f, 1. / self.output_samples)

            V = np.append(
                V, Amplitudefreaction * self.A * np.sin(2 * np.pi * f * t)
            )

            T = np.append(T, t + t0)
            t0 += t[-1]

        return -V - self.A, T

    def get_settings_as_dict(self):
        pulse_parameters = {
            "Intensity_v": self.A,
            "Waveform": self.Waveform,
            "Period_s": self.Duration,
            "Offset_Before_ms": self.Offset_Before,
            "Offset_After_ms": self.Offset_After
        }
        return pulse_parameters

    def get_total_duration(self):
        return self.Duration + self.Offset_Before + self.Offset_After

    def last_t(self):
        return self.time_array[-1]
