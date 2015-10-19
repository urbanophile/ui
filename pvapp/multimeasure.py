import wx
from gui.new_gui import IncrementalApp


class View1(IncrementalApp):
    def __init__(self, parent):
        IncrementalApp.__init__(self, parent)

    def _set_ui_validators(self):
        pass

    def get_ui_input(self):
        pass

    def set_ui_input(self):
        pass

class Controller(object):
    """docstring for Controller"""
    def __init__(self, app):
        super(Controller, self).__init__()
        self.view1 = View1(None)

        self._set_event_bindings()
        self.view1.Show()

    def save_settings(self):
        pass

    def load_settings(self):
        pass

    def hard_mode(self):
        pass

    def display(self):
        pass

    def perform_experiment(self):
        pass

    def _set_event_bindings(self):

        self.view1.m_save.Bind(wx.EVT_BUTTON, self.save_settings)
        self.view1.m_load.Bind(wx.EVT_BUTTON, self.load_settings)
        self.view1.m_hardMode.Bind(wx.EVT_BUTTON, self.hard_mode)
        self.view1.m_display.Bind(wx.EVT_BUTTON, self.display)
        self.view1.m_performExperiment.Bind(wx.EVT_BUTTON,
                                            self.perform_experiment)

    def _parse_settings(self):
        pass


if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    app.MainLoop()
