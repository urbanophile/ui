import wx
import matplotlib.figure as plt
import numpy as np
# from gui.Canvas import CanvasPanel
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from util.Models import ExperimentData
import wx.lib.inspection


ID_OK_BUTTON = wx.NewId()
ID_CLOSE_BUTTON = wx.NewId()

SLIDER_MIN = 0
SLIDER_MAX = 100
SLIDER_INITIAL = 100
HEIGHT = 2

def enum(**enums):
    return type('Enum', (), enums)

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

        self.Data = ExperimentData()

        # Attributes
        self.tc_x_mouse = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.tc_y_mouse = wx.TextCtrl(self, style=wx.TE_READONLY)

        # display offsets
        self.tc_x_start = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.tc_x_end = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.tc_y = wx.TextCtrl(self, style=wx.TE_READONLY)

        # Matplotlib canvas
        self.figure = plt.Figure()

        # action types
        self.action_types = ['none', 'start x', 'end x', 'y']
        self.combobox = wx.ComboBox(
            self, choices=self.action_types, style=wx.CB_READONLY
        )

        # mouse action state
        self.mouse_action = None
        # Layout
        self._PlotHandler()
        self._doLayout()

        # Event Handlers
        self._EventHandlers()


    def _doLayout(self):

        # self.SetBackgroundColour('#ffff00')

        vbox = wx.BoxSizer(wx.VERTICAL)

        # layout for matplotlib canvas
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # self.Fig1 = CanvasPanel(canvas_panel)

        hbox1.Add(self.figure_canvas, proportion=1, flag=wx.ALL|wx.EXPAND, border=20)
        vbox.Add(hbox1, proportion=1, flag=wx.EXPAND, border=20)

        vbox.AddSpacer(15)

        # layout for x,y coordinates
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        fields = wx.FlexGridSizer(3, 2, 9, 25)

        x_label = wx.StaticText(self, label='x:')
        y_label = wx.StaticText(self, label='y:')
        mouse_label = wx.StaticText(self, label='Mouse Coordinates')

        fields.AddMany([
            wx.StaticText(self, label=''), mouse_label,
            (x_label), (self.tc_x_mouse, 1, wx.EXPAND),
            (y_label), (self.tc_y_mouse, 1, wx.EXPAND),
        ])
        hbox2.Add(fields, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        # layout for mouse action
        hbox2_b = wx.BoxSizer(wx.VERTICAL)
        combo_label = wx.StaticText(self, label='Click Action')

        hbox2_b.AddMany([combo_label, self.combobox])
        hbox2.Add(hbox2_b, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        # layout for offset selection
        fields_offset = wx.FlexGridSizer(4, 2, 9, 25)

        offset_label = wx.StaticText(self, label='Offset')
        x_start_label = wx.StaticText(self, label='start x')
        x_end_label = wx.StaticText(self, label='end x')
        y_label = wx.StaticText(self, label='y')

        fields_offset.AddMany([
            wx.StaticText(self, label=''), offset_label,
            x_start_label, self.tc_x_start,
            x_end_label, self.tc_x_end,
            y_label, self.tc_y,

        ])

        hbox2.Add(fields_offset, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        vbox.Add(hbox2, flag=wx.EXPAND, border=20)

        # for spacing
        vbox.AddSpacer(25)

        # layout for open close buttons
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.okButton = wx.Button(self, id=ID_OK_BUTTON, label='Ok')
        self.closeButton = wx.Button(self, id=ID_CLOSE_BUTTON, label='Close')
        hbox3.Add(self.okButton)
        hbox3.Add(self.closeButton, flag=wx.LEFT | wx.BOTTOM, border=5)
        vbox.Add(hbox3, flag=wx.ALIGN_CENTER, border=10)

        # add in slider
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.slider = wx.Slider(self, value=SLIDER_INITIAL, minValue=SLIDER_MIN, maxValue=SLIDER_MAX, pos=(20, 20),
                                size=(250, -1), style=wx.SL_HORIZONTAL)
        hbox4.Add(self.slider)
        vbox.Add(hbox4, flag=wx.ALIGN_CENTER, border=10)

        # add in buttons
        self.SetSizer(vbox)

    def _PlotHandler(self):
        x = [SLIDER_INITIAL] * HEIGHT
        y = range(HEIGHT)
        # so that it's a tuple

        # matplotlib canvas
        self.axes1 = self.figure.add_subplot(111)
        self.figure_canvas = FigureCanvas(self, -1, self.figure)
        self.figure.canvas.mpl_connect('motion_notify_event', self.OnMove)
        self.figure.canvas.mpl_connect('button_press_event', self.OnClick)

        self.figure_canvas.line, = self.axes1.plot(x, y, linewidth=2)

        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']
        data = self.Data.Data
        for i, label, colour in zip(data[:, 1:].T, labels, colours):

            self.axes1.plot(
                data[::1, 0],
                i[::1],
                '.',
                # Color=colour,
                # Label=label
            )


    def _EventHandlers(self):
        self.okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        self.combobox.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.combobox.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll)



    def OnClose(self, e):
        print("OnClose")
        self.GetParent().Close()
        # e.skip()

    def OnMove(self, plt_event):
        x_coord = plt_event.xdata
        y_coord = plt_event.ydata
        log_format = 'button={0}, x={1}, y={2}, xdata={3}, ydata={4}'
        # print(log_format.format(
        #     plt_event.button, plt_event.x, plt_event.y,
        #     plt_event.xdata, plt_event.ydata
        # ))
        if x_coord is not None and y_coord is not None:
            self.tc_x_mouse.SetValue('{0:.2f}'.format(x_coord))
            self.tc_y_mouse.SetValue('{0:.2f}'.format(y_coord))

    def OnClick(self, plt_event):
        x_coord = plt_event.xdata
        y_coord = plt_event.ydata
        log_format = 'button={0}, x={1}, y={2}, xdata={3}, ydata={4}'
        print(log_format.format(
            plt_event.button, plt_event.x, plt_event.y,
            plt_event.xdata, plt_event.ydata
        ))
        if x_coord is not None and y_coord is not None:
            if self.mouse_action == 'start x':
                self.tc_x_start.SetValue('{0:.2f}'.format(x_coord))
            elif self.mouse_action == 'end x':
                self.tc_x_end.SetValue('{0:.2f}'.format(x_coord))
            elif self.mouse_action == 'y':
                self.tc_y.SetValue('{0:.2f}'.format(y_coord))

    def OnSelect(self, e):
        combo_selection = e.GetString()
        self.mouse_action = combo_selection

    def move_left(self, val):
        # print("DEBUG VAL: ", val)
        x, y = self.figure_canvas.line.get_data()
        # print("DEBUG: ", x, y)
        x = [val] * HEIGHT
        self.figure_canvas.line.set_xdata(np.array(x) + 0.001)
        # self.axes1.set_xbound([0, x[-1] + 1])
        self.figure_canvas.draw()

    def offset_mean(self, val, col_num):
        """
        Determine mean value of col_num column between val to end of the array
        """
        col = self.Data.Data[:, col_num]
        fudge_factor = len(col) / float(SLIDER_MAX)
        # print(col)
        return np.min(col[int(fudge_factor) * val:])

    def update_graph(self, mean_val, col_num):
        labels = ['Reference', 'PC', 'PL']
        colours = ['b', 'r', 'g']
        data = np.copy(self.Data.Data)
        data[:, col_num] = self.Data.Data[:, col_num] - mean_val
        for i, label, colour in zip(data[:, 1:].T, labels, colours):

            self.axes1.plot(
                data[::1, 0],
                i[::1],
                '.',
                color=colour,
                # Label=label
            )
        del self.axes1.lines[1:4]
        # self.figure_canvas.draw()

    def OnSliderScroll(self, e):

        obj = e.GetEventObject()
        val = obj.GetValue()
        mean_val = self.offset_mean(val, 1)
        self.update_graph(mean_val, 1)
        print(self.axes1.lines)
        self.move_left(val)
        print(str(val))
        print(mean_val)

        # self.txt.SetLabel(str(val))



def main():

    ex = wx.App(False)
    BoxSizerFrame(None)
    # wx.lib.inspection.InspectionTool().Show()
    ex.MainLoop()


if __name__ == '__main__':
    main()
