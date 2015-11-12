from util.Exceptions import PVInputError


class TemperatureSettings(object):
    """
    Contains information for temperature change for a series of experiments
    """

    def __init__(self, start_temp, end_temp, step_temp):
        super(TemperatureSettings, self).__init__()

        temp_diff = abs(start_temp - end_temp)
        if step_temp > temp_diff:
            raise PVInputError(
                "Step size is larger than the temperature difference."
            )

        if temp_diff != 0 and temp_diff % step_temp != 0:
            raise PVInputError(
                "Step size doesn't evenly divide temperature difference."
            )

        if start_temp == end_temp and step_temp != 0:
            raise PVInputError(
                "Can't take that many steps in that between start and end."
            )

        self.start_temp = start_temp
        self.end_temp = end_temp
        self.step_temp = step_temp

    def as_dict(self):
        return {
            "start_temp": self.start_temp,
            "end_temp": self.end_temp,
            "step_temp": self.step_temp
        }

    def __repr__(self):
        return "{0}".format(self.__dict__())
