import wx
import matplotlib.figure as plt
# from gui.Canvas import CanvasPanel
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx.lib.inspection

ID_OK_BUTTON = wx.NewId()
ID_CLOSE_BUTTON = wx.NewId()


class BoxSizerFrame(wx.Frame):

    def __init__(self, parent, *args, **kwargs):
        super(BoxSizerFrame, self).__init__(parent, *args, **kwargs)

        # Attributes
        self.panel = BoxSizerPanel(self)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()
        self.Show()


class BoxSizerPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super(BoxSizerPanel, self).__init__(parent, *args, **kwargs)

        # Attributes
        self.tc_x_start = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.tc_y_start = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.figure = plt.Figure()

        # Layout
        self._doLayout()

        # Event Handlers
        self._EventHandlers()

    def _doLayout(self):

        # self.SetBackgroundColour('#ffff00')

        vbox = wx.BoxSizer(wx.VERTICAL)

        # layout for matplotlib canvas
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # self.Fig1 = CanvasPanel(canvas_panel)

        # matplotlib canvas
        axes1 = self.figure.add_subplot(111)
        figure_canvas = FigureCanvas(self, -1, self.figure)
        self.figure.canvas.mpl_connect('button_press_event', self.OnClick)


        hbox1.Add(figure_canvas, proportion=1, flag=wx.ALL|wx.EXPAND, border=20)
        vbox.Add(hbox1, proportion=1, flag=wx.EXPAND, border=20)

        vbox.AddSpacer(15)

        # layout for x,y coordinates
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        fields = wx.FlexGridSizer(2, 2, 9, 25)

        x_start_label = wx.StaticText(self, label='x:')
        y_start_label = wx.StaticText(self, label='y:')

        fields.AddMany([
            (x_start_label), (self.tc_x_start, 1, wx.EXPAND),
            (y_start_label), (self.tc_y_start, 1, wx.EXPAND),
        ])
        hbox2.Add(fields, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        vbox.Add(hbox2, flag=wx.EXPAND, border=20)

        # for spacing
        vbox.AddSpacer(25)

        # layout for open close buttons
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.okButton = wx.Button(self, id=ID_OK_BUTTON, label='Ok')
        self.closeButton = wx.Button(self, id=ID_CLOSE_BUTTON, label='Close')
        hbox3.Add(self.okButton)
        hbox3.Add(self.closeButton, flag=wx.LEFT|wx.BOTTOM, border=5)
        vbox.Add(hbox3, flag=wx.ALIGN_CENTER, border=10)

        self.SetSizer(vbox)

        # event handlers

    def _EventHandlers(self):
        self.okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):
        print("OnClose")
        self.GetParent().Close()
        # e.skip()

    def OnClick(self, plt_event):
        x_coord = plt_event.xdata
        y_coord = plt_event.ydata
        log_format = 'button={0}, x={1}, y={2}, xdata={3}, ydata={4}'
        print(log_format.format(
            plt_event.button, plt_event.x, plt_event.y,
            plt_event.xdata, plt_event.ydata
        ))
        if x_coord is not None and y_coord is not None:
            self.tc_x_start.SetValue('{0:.2f}'.format(x_coord))
            self.tc_y_start.SetValue('{0:.2f}'.format(y_coord))



def main():

    ex = wx.App(False)
    BoxSizerFrame(None)
    # wx.lib.inspection.InspectionTool().Show()
    ex.MainLoop()


if __name__ == '__main__':
    main()
