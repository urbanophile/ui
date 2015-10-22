class Wafer(object):
    """Physical Properties of the Wafer"""
    def __init__(self, thickness, codoped, na, nd,
                 diffused, num_sides):
        super(Wafer, self).__init__()

        self._thickness = thickness
        self._codoped = codoped
        self._na = na
        self._nd = nd
        self._diffused = diffused
        self._num_sides = num_sides

    @property
    def thickness(self):
        """thickness of the wafer (in mm)"""
        return self._thickness

    @property
    def codoped(self):
        """Unclear what this means"""
        return self._codoped

    @property
    def na(self):
        """acceptor concentration"""
        return self._na

    @property
    def nd(self):
        """donor concentration"""
        return self._nd

    @property
    def diffused(self):
        """Unclear what this means"""
        return self._diffused

    @property
    def num_sides(self):
        """Number of sides on which it's diffused"""
        return self._num_sides
