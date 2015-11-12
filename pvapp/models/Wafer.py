class Wafer(object):
    """Physical properties of the silicon wafer"""

    def __init__(self, wafer_id, thickness, na, nd,
                 diffused, num_sides):
        """
            id: identifier for wafer
            thickness: thickness of the wafer (in mm)
=            na: acceptor (boron) concentration
            nd: donor (phosphorus) concentration
            diffused: has N or P type layer
            num_sides: Number of sides on which it's diffused
        """
        self.id = wafer_id
        self.thickness = thickness
        self.na = na
        self.nd = nd
        self.diffused = diffused
        self.num_sides = num_sides

    def as_dict(self):
        return {
            "wafer_id": self.id,
            "wafer_thickness": self.thickness,
            "wafer_na": self.na,
            "wafer_nd": self.nd,
            "wafer_diffused": self.diffused,
            "wafer_num_sides": self.num_sides
        }
