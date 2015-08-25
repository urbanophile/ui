import wx


class ChangeDepthDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(ChangeDepthDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Offsets")

    def InitUI(self):

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.RadioButton(panel, label='Custom'))
        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)

        tc_x_start = wx.TextCtrl(self, style=wx.TE_READONLY)
        tc_y_start = wx.TextCtrl(self, style=TE_READONLY)
        tc_x_end = wx.TextCtrl(self, style=TE_READONLY)
        tc_y_end = wx.TextCtrl(self, style=TE_READONLY)

        x_start_label = wx.StaticText(self, 'x:')
        y_start_label = wx.StaticText(self, 'y:')

        x_end_label = wx.StaticText(self, 'x:')
        y_end_label = wx.StaticText(self, 'y:')

        sb_start = wx.StaticBox(panel, label="Initial Offset")
        boxsizer_start = wx.StaticBoxSizer(sb, wx.VERTICAL)

        sb_end = wx.StaticBox(panel, label="Final Offset")
        boxsizer_end = wx.StaticBoxSizer(sb, wx.VERTICAL)

        sb_start.Add(tc_x_start)
        sb_start.Add(tc_x_start)

        panel.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2,
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        # event handlers
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):
        self.Destroy()
