class TemperatureSettings(object):
    """
    Contains information for temperature change for a series of experiments
    """
    def __init__(self, start_temp, end_temp, step_temp):
        super(TemperatureSettings, self).__init__()

        self.start_temp = start_temp
        self.end_temp = end_temp
        self.step_temp = step_temp

    def __repr__(self):
        return "{0}".format(self.__dict__())

