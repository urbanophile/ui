import wx
from Canvas import CanvasPanel


class PlotModal(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, size=(600, 600), title='Display Waveforms')
        self.parent = parent
        self.panel = wx.Panel(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.Fig1 = CanvasPanel(self.panel)

        self.m_ok_button = wx.Button(parent=self.panel, id=-1, label='Ok')

        self.sizer.Add(
            item=self.Fig1,
            proportion=1,
            flag=wx.ALL
        )

        self.sizer.AddSpacer((10, 10), 1, wx.EXPAND, 10)

        self.sizer.Add(
            item=self.m_ok_button,
            proportion=1,
            flag=wx.CENTER | wx.ALL
        )

        self.sizer.AddSpacer((10, 10), 1, wx.EXPAND, 10)

        self.panel.SetSizer(self.sizer)

        self.panel.Fit()

        # event bindings
        self.m_ok_button.Bind(wx.EVT_BUTTON, self.ok_button)

    def ok_button(self, evt):
        self.Destroy()

    def clear_figure(self):
        self.Fig1.clear()

    def plot_data(self, data):
        self.colours = ["r", "g", "b"]
        # This plots the figure
        for index, column in enumerate(data):

            self.Fig1.draw_points(
                range(len(column)),
                column,
                '.',
                Color=self.colours[index]
            )

        self.Fig1.update()


if __name__ == '__main__':

    app = wx.App()
    app.MainLoop()
