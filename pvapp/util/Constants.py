CHANNELS = ['Reference', 'PC', 'PL']
CHANNEL_INDEX = {
    'Reference': 1,
    'PC': 2,
    'PL': 3
}

INPUT_VOLTAGE_RANGE = [10, 5, 2, 1]
INPUT_VOLTAGE_RANGE_STR = ['+/- 10', '+/- 5', '+/- 2', '+/- 1']

OUTPUT_VOLTAGE_RANGE = 5

WAVEFORMS = ["Cos", "Sin", "Square",
             "Triangle", "MattiasCustom", "FrequencyScan"]
OUTPUTS = ['Low (50mA/V)', 'High (2A/V)']


# These values are specific to NI-DAQmx

# Magic numbers relating to hardware. They convert sent voltage to current.
# They are determined by experimental measurement
HIGH_HARDWARE_CONST = 1840.
LOW_HARDWARE_CONST = 66.

# A 10V limit is imposed due to limited the output voltage of the datacard
LOW_VOLTAGE_LIMIT = 10

# A 1.5V limit is imposed as a limit owing to the current limit of
# the power supply.
HIGH_VOLTAGE_LIMIT = 1.5

# Constant that works, so the threshold doesn't get to big
THRESHOLD_CONST = 5


# Max is float64(1e6), well its 1.25MS/s/channel
MAX_INPUT_SAMPLE_RATE = 1.2e6
# It's 3.33MS/s
MAX_OUTPUT_SAMPLE_RATE = 1.2e6
