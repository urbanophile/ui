class Wafer(object):
    """Physical properties of the silicon wafer"""

    def __init__(self, thickness, codoped, na, nd,
                 diffused, num_sides):
        """
            thickness: thickness of the wafer (in mm)
            codoped: unclear what this means
            na: acceptor concentration
            nd: donor concentration
            diffused: unclear what this means
            num_sides: Number of sides on which it's diffused
        """

        self.thickness = thickness
        self.codoped = codoped
        self.na = na
        self.nd = nd
        self.diffused = diffused
        self.num_sides = num_sides

    def as_dict(self):
        return {
            "thickness": self.thickness,
            "codoped": self.codoped,
            "na": self.na,
            "nd": self.nd,
            "diffused": self.diffused,
            "num_sides": self.num_sides
        }
