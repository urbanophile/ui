# -*- coding: utf-8 -*- ############################################################################# Python code generated with wxFormBuilder (version Sep 12 2010)## http://www.wxformbuilder.org/#### PLEASE DO "NOT" EDIT THIS FILE!###########################################################################import wx############################################################################# Class MyFrame1###########################################################################class MyFrame1 ( wx.Frame ):		def __init__( self, parent ):		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )				self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )				bSizer1 = wx.BoxSizer( wx.VERTICAL )				self.SetSizer( bSizer1 )		self.Layout()				self.Centre( wx.BOTH )		def __del__( self ):		pass	############################################################################# Class MyPanel1###########################################################################class MyPanel1 ( wx.Panel ):		def __init__( self, parent ):		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )				bSizer2 = wx.BoxSizer( wx.VERTICAL )				fgSizer4 = wx.FlexGridSizer( 3, 1, 0, 0 )		fgSizer4.SetFlexibleDirection( wx.BOTH )		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				fgSizer1 = wx.FlexGridSizer( 2, 4, 0, 0 )		fgSizer1.SetFlexibleDirection( wx.BOTH )		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )						fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )				self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Start Temp", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText2.Wrap( -1 )		fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )				self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"End Temp", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText3.Wrap( -1 )		fgSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )				self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText4.Wrap( -1 )		fgSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )				self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Temperature", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText1.Wrap( -1 )		fgSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )				self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_textCtrl1, 0, wx.ALL, 5 )				self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_textCtrl2, 0, wx.ALL, 5 )				self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_textCtrl3, 0, wx.ALL, 5 )				fgSizer4.Add( fgSizer1, 1, wx.EXPAND, 5 )				fgSizer2 = wx.FlexGridSizer( 2, 12, 0, 0 )		fgSizer2.SetFlexibleDirection( wx.BOTH )		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )						fgSizer2.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )				self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Waveform", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText6.Wrap( -1 )		fgSizer2.Add( self.m_staticText6, 0, wx.ALL, 5 )				self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Period", wx.DefaultPosition, wx.Size( 50,-1 ), 0 )		self.m_staticText7.Wrap( -1 )		fgSizer2.Add( self.m_staticText7, 0, wx.ALL, 5 )				self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Amplitude", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText8.Wrap( -1 )		fgSizer2.Add( self.m_staticText8, 0, wx.ALL, 5 )				self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Offset1", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText9.Wrap( -1 )		fgSizer2.Add( self.m_staticText9, 0, wx.ALL, 5 )				self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"Offset2", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText10.Wrap( -1 )		fgSizer2.Add( self.m_staticText10, 0, wx.ALL, 5 )				self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText11.Wrap( -1 )		fgSizer2.Add( self.m_staticText11, 0, wx.ALL, 5 )				self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText12.Wrap( -1 )		fgSizer2.Add( self.m_staticText12, 0, wx.ALL, 5 )				self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText13.Wrap( -1 )		fgSizer2.Add( self.m_staticText13, 0, wx.ALL, 5 )				self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText14.Wrap( -1 )		fgSizer2.Add( self.m_staticText14, 0, wx.ALL, 5 )				self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText15.Wrap( -1 )		fgSizer2.Add( self.m_staticText15, 0, wx.ALL, 5 )				self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText16.Wrap( -1 )		fgSizer2.Add( self.m_staticText16, 0, wx.ALL, 5 )				bSizer4 = wx.BoxSizer( wx.VERTICAL )				self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer4.Add( self.m_checkBox1, 0, wx.ALL, 5 )				self.m_checkBox2 = wx.CheckBox( self, wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer4.Add( self.m_checkBox2, 0, wx.ALL, 5 )				self.m_checkBox3 = wx.CheckBox( self, wx.ID_ANY, u"3", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer4.Add( self.m_checkBox3, 0, wx.ALL, 5 )				self.m_checkBox4 = wx.CheckBox( self, wx.ID_ANY, u"4", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer4.Add( self.m_checkBox4, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer4, 1, wx.EXPAND, 5 )				bSizer5 = wx.BoxSizer( wx.VERTICAL )				m_choice2Choices = []		self.m_choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )		self.m_choice2.SetSelection( 0 )		bSizer5.Add( self.m_choice2, 0, wx.ALL, 5 )				m_choice3Choices = []		self.m_choice3 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )		self.m_choice3.SetSelection( 0 )		bSizer5.Add( self.m_choice3, 0, wx.ALL, 5 )				m_choice4Choices = []		self.m_choice4 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice4Choices, 0 )		self.m_choice4.SetSelection( 0 )		bSizer5.Add( self.m_choice4, 0, wx.ALL, 5 )				m_choice5Choices = []		self.m_choice5 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice5Choices, 0 )		self.m_choice5.SetSelection( 0 )		bSizer5.Add( self.m_choice5, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer5, 1, wx.EXPAND, 5 )				bSizer6 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_textCtrl4.SetMaxSize( wx.Size( 50,50 ) )				bSizer6.Add( self.m_textCtrl4, 0, wx.ALL, 5 )				self.m_textCtrl5 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_textCtrl5.SetMaxSize( wx.Size( 50,-1 ) )				bSizer6.Add( self.m_textCtrl5, 0, wx.ALL, 5 )				self.m_textCtrl6 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_textCtrl6.SetMaxSize( wx.Size( 50,-1 ) )				bSizer6.Add( self.m_textCtrl6, 0, wx.ALL, 5 )				self.m_textCtrl7 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_textCtrl7.SetMaxSize( wx.Size( 50,-1 ) )				bSizer6.Add( self.m_textCtrl7, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer6, 1, wx.EXPAND, 5 )				bSizer61 = wx.BoxSizer( wx.VERTICAL )				bSizer61.SetMinSize( wx.Size( 50,-1 ) ) 		self.m_textCtrl41 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer61.Add( self.m_textCtrl41, 0, wx.ALL, 5 )				self.m_textCtrl51 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer61.Add( self.m_textCtrl51, 0, wx.ALL, 5 )				self.m_textCtrl61 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer61.Add( self.m_textCtrl61, 0, wx.ALL, 5 )				self.m_textCtrl71 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer61.Add( self.m_textCtrl71, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer61, 1, wx.EXPAND, 5 )				bSizer611 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl411 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer611.Add( self.m_textCtrl411, 0, wx.ALL, 5 )				self.m_textCtrl511 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer611.Add( self.m_textCtrl511, 0, wx.ALL, 5 )				self.m_textCtrl611 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer611.Add( self.m_textCtrl611, 0, wx.ALL, 5 )				self.m_textCtrl711 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer611.Add( self.m_textCtrl711, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer611, 1, wx.EXPAND, 5 )				bSizer612 = wx.BoxSizer( wx.VERTICAL )				bSizer612.SetMinSize( wx.Size( 50,-1 ) ) 		self.m_textCtrl412 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer612.Add( self.m_textCtrl412, 0, wx.ALL, 5 )				self.m_textCtrl512 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer612.Add( self.m_textCtrl512, 0, wx.ALL, 5 )				self.m_textCtrl612 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer612.Add( self.m_textCtrl612, 0, wx.ALL, 5 )				self.m_textCtrl712 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer612.Add( self.m_textCtrl712, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer612, 1, wx.EXPAND, 5 )				bSizer613 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl413 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer613.Add( self.m_textCtrl413, 0, wx.ALL, 5 )				self.m_textCtrl513 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer613.Add( self.m_textCtrl513, 0, wx.ALL, 5 )				self.m_textCtrl613 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer613.Add( self.m_textCtrl613, 0, wx.ALL, 5 )				self.m_textCtrl713 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer613.Add( self.m_textCtrl713, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer613, 1, wx.EXPAND, 5 )				bSizer614 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl414 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer614.Add( self.m_textCtrl414, 0, wx.ALL, 5 )				self.m_textCtrl514 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer614.Add( self.m_textCtrl514, 0, wx.ALL, 5 )				self.m_textCtrl614 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer614.Add( self.m_textCtrl614, 0, wx.ALL, 5 )				self.m_textCtrl714 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer614.Add( self.m_textCtrl714, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer614, 1, wx.EXPAND, 5 )				bSizer51 = wx.BoxSizer( wx.VERTICAL )				m_choice21Choices = []		self.m_choice21 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice21Choices, 0 )		self.m_choice21.SetSelection( 0 )		bSizer51.Add( self.m_choice21, 0, wx.ALL, 5 )				m_choice31Choices = []		self.m_choice31 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice31Choices, 0 )		self.m_choice31.SetSelection( 0 )		bSizer51.Add( self.m_choice31, 0, wx.ALL, 5 )				m_choice41Choices = []		self.m_choice41 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice41Choices, 0 )		self.m_choice41.SetSelection( 0 )		bSizer51.Add( self.m_choice41, 0, wx.ALL, 5 )				m_choice51Choices = []		self.m_choice51 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice51Choices, 0 )		self.m_choice51.SetSelection( 0 )		bSizer51.Add( self.m_choice51, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer51, 1, wx.EXPAND, 5 )				bSizer6141 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl4141 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6141.Add( self.m_textCtrl4141, 0, wx.ALL, 5 )				self.m_textCtrl5141 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6141.Add( self.m_textCtrl5141, 0, wx.ALL, 5 )				self.m_textCtrl6141 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6141.Add( self.m_textCtrl6141, 0, wx.ALL, 5 )				self.m_textCtrl7141 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6141.Add( self.m_textCtrl7141, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer6141, 1, wx.EXPAND, 5 )				bSizer6142 = wx.BoxSizer( wx.VERTICAL )				self.m_textCtrl4142 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6142.Add( self.m_textCtrl4142, 0, wx.ALL, 5 )				self.m_textCtrl5142 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6142.Add( self.m_textCtrl5142, 0, wx.ALL, 5 )				self.m_textCtrl6142 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6142.Add( self.m_textCtrl6142, 0, wx.ALL, 5 )				self.m_textCtrl7142 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer6142.Add( self.m_textCtrl7142, 0, wx.ALL, 5 )				fgSizer2.Add( bSizer6142, 1, wx.EXPAND, 5 )				fgSizer4.Add( fgSizer2, 1, wx.EXPAND, 2 )				fgSizer3 = wx.FlexGridSizer( 1, 5, 0, 0 )		fgSizer3.SetFlexibleDirection( wx.BOTH )		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_button4 = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer3.Add( self.m_button4, 0, wx.ALL, 5 )				self.m_button5 = wx.Button( self, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer3.Add( self.m_button5, 0, wx.ALL, 5 )				self.m_button6 = wx.Button( self, wx.ID_ANY, u"Extreme", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer3.Add( self.m_button6, 0, wx.ALL, 5 )				self.m_button7 = wx.Button( self, wx.ID_ANY, u"View Waveforms", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer3.Add( self.m_button7, 0, wx.ALL, 5 )				self.m_button8 = wx.Button( self, wx.ID_ANY, u"Run experiments", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer3.Add( self.m_button8, 0, wx.ALL, 5 )				fgSizer4.Add( fgSizer3, 1, wx.EXPAND, 5 )				bSizer2.Add( fgSizer4, 1, wx.EXPAND, 5 )				self.SetSizer( bSizer2 )		self.Layout()		bSizer2.Fit( self )		def __del__( self ):		pass	############################################################################# Class HardwarePanel###########################################################################class HardwarePanel ( wx.Panel ):		def __init__( self, parent ):		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )				bSizer3 = wx.BoxSizer( wx.HORIZONTAL )				fgSizer5 = wx.FlexGridSizer( 5, 1, 0, 0 )		fgSizer5.SetFlexibleDirection( wx.BOTH )		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_button10 = wx.Button( self, wx.ID_ANY, u"PC Calibration", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button10, 0, wx.ALL, 5 )				bSizer15 = wx.BoxSizer( wx.HORIZONTAL )				self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, u"PL Calibration Method", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText17.Wrap( -1 )		bSizer15.Add( self.m_staticText17, 0, wx.ALL, 5 )				m_plCalibrationMethodChoices = []		self.m_plCalibrationMethod = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_plCalibrationMethodChoices, 0 )		self.m_plCalibrationMethod.SetSelection( 0 )		bSizer15.Add( self.m_plCalibrationMethod, 0, wx.ALL, 5 )				fgSizer5.Add( bSizer15, 1, wx.EXPAND, 5 )				self.m_button13 = wx.Button( self, wx.ID_ANY, u"Perform PC Calibration", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button13, 0, wx.ALL, 5 )				self.m_button14 = wx.Button( self, wx.ID_ANY, u"View Calibration Const", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button14, 0, wx.ALL, 5 )				self.m_button15 = wx.Button( self, wx.ID_ANY, u"Calibrate Stage", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button15, 0, wx.ALL, 5 )				self.m_button121 = wx.Button( self, wx.ID_ANY, u"Calibrate FS.", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button121, 0, wx.ALL, 5 )				bSizer3.Add( fgSizer5, 1, wx.EXPAND, 5 )				fgSizer7 = wx.FlexGridSizer( 2, 1, 0, 0 )		fgSizer7.SetFlexibleDirection( wx.BOTH )		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Wafer Parameters" ), wx.VERTICAL )				fgSizer6 = wx.FlexGridSizer( 2, 2, 0, 0 )		fgSizer6.SetFlexibleDirection( wx.BOTH )		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"Thickness (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText16.Wrap( -1 )		fgSizer6.Add( self.m_staticText16, 0, wx.ALL, 5 )				self.m_textCtrl36 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_textCtrl36, 0, wx.ALL, 5 )				self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, u"Co-doped", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText20.Wrap( -1 )		fgSizer6.Add( self.m_staticText20, 0, wx.ALL, 5 )				m_choice11Choices = []		self.m_choice11 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice11Choices, 0 )		self.m_choice11.SetSelection( 0 )		fgSizer6.Add( self.m_choice11, 0, wx.ALL, 5 )				self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, u"Na", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText22.Wrap( -1 )		fgSizer6.Add( self.m_staticText22, 0, wx.ALL, 5 )				self.m_textCtrl39 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_textCtrl39, 0, wx.ALL, 5 )				self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Nd", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText23.Wrap( -1 )		fgSizer6.Add( self.m_staticText23, 0, wx.ALL, 5 )				self.m_textCtrl40 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_textCtrl40, 0, wx.ALL, 5 )				self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, u"Diffused", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText21.Wrap( -1 )		fgSizer6.Add( self.m_staticText21, 0, wx.ALL, 5 )				m_choice12Choices = []		self.m_choice12 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice12Choices, 0 )		self.m_choice12.SetSelection( 0 )		fgSizer6.Add( self.m_choice12, 0, wx.ALL, 5 )				self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"# of Sides", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText24.Wrap( -1 )		fgSizer6.Add( self.m_staticText24, 0, wx.ALL, 5 )				m_choice101Choices = []		self.m_choice101 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice101Choices, 0 )		self.m_choice101.SetSelection( 0 )		fgSizer6.Add( self.m_choice101, 0, wx.ALL, 5 )				sbSizer1.Add( fgSizer6, 1, wx.EXPAND, 5 )				fgSizer7.Add( sbSizer1, 1, wx.EXPAND, 5 )				fgSizer8 = wx.FlexGridSizer( 2, 2, 0, 0 )		fgSizer8.SetFlexibleDirection( wx.BOTH )		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_staticText18 = wx.StaticText( self, wx.ID_ANY, u"Waffer ID", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText18.Wrap( -1 )		fgSizer8.Add( self.m_staticText18, 0, wx.ALL, 5 )				self.m_textCtrl37 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer8.Add( self.m_textCtrl37, 0, wx.ALL, 5 )				self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, u"File Directory", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText19.Wrap( -1 )		fgSizer8.Add( self.m_staticText19, 0, wx.ALL, 5 )				self.m_textCtrl38 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer8.Add( self.m_textCtrl38, 0, wx.ALL, 5 )				fgSizer7.Add( fgSizer8, 1, wx.EXPAND, 5 )				self.m_button12 = wx.Button( self, wx.ID_ANY, u"Perform Measurement", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer7.Add( self.m_button12, 0, wx.ALL, 5 )				bSizer3.Add( fgSizer7, 1, wx.EXPAND, 5 )				self.SetSizer( bSizer3 )		self.Layout()		bSizer3.Fit( self )		def __del__( self ):		pass	############################################################################# Class IncrementalApp###########################################################################class IncrementalApp ( wx.Frame ):		def __init__( self, parent ):		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"IncrementalApp", pos = wx.DefaultPosition, size = wx.Size( 850,400 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )				self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )				main_hbox = wx.BoxSizer( wx.VERTICAL )				self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_hardwarePanel = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )				fgSizer5 = wx.FlexGridSizer( 6, 1, 0, 0 )		fgSizer5.SetFlexibleDirection( wx.VERTICAL )		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_calibratePC = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Calibrate PC", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_calibratePC, 0, wx.ALL, 5 )				bSizer15 = wx.BoxSizer( wx.HORIZONTAL )				self.m_staticText17 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"PL Calibration Method", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText17.Wrap( -1 )		bSizer15.Add( self.m_staticText17, 0, wx.ALL, 5 )				m_plCalibrationMethodChoices = []		self.m_plCalibrationMethod = wx.Choice( self.m_hardwarePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_plCalibrationMethodChoices, 0 )		self.m_plCalibrationMethod.SetSelection( 0 )		bSizer15.Add( self.m_plCalibrationMethod, 0, wx.ALL, 5 )				fgSizer5.Add( bSizer15, 1, wx.EXPAND, 5 )				self.m_button13 = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Calibrate PL", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button13, 0, wx.ALL, 5 )				self.m_button15 = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Calibrate Stage", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button15, 0, wx.ALL, 5 )				self.m_button121 = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Calibrate FS.", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_button121, 0, wx.ALL, 5 )				self.m_showCalibrationConst = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"View Calibration Const", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer5.Add( self.m_showCalibrationConst, 0, wx.ALL, 5 )				bSizer3.Add( fgSizer5, 0, wx.EXPAND, 5 )				fgSizer7 = wx.FlexGridSizer( 3, 1, 0, 0 )		fgSizer7.SetFlexibleDirection( wx.BOTH )		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_hardwarePanel, wx.ID_ANY, u"Wafer Parameters" ), wx.VERTICAL )				fgSizer6 = wx.FlexGridSizer( 6, 2, 0, 0 )		fgSizer6.SetFlexibleDirection( wx.BOTH )		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_staticText18 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Wafer ID", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText18.Wrap( -1 )		fgSizer6.Add( self.m_staticText18, 0, wx.ALL, 5 )				self.m_waferID = wx.TextCtrl( self.m_hardwarePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_waferID, 0, wx.ALL, 5 )				self.m_staticText16 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Thickness (mm)", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText16.Wrap( -1 )		fgSizer6.Add( self.m_staticText16, 0, wx.ALL, 5 )				self.m_waferThickness = wx.TextCtrl( self.m_hardwarePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_waferThickness, 0, wx.ALL, 5 )				self.m_staticText20 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Co-doped", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText20.Wrap( -1 )		fgSizer6.Add( self.m_staticText20, 0, wx.ALL, 5 )				m_waferCodopedChoices = []		self.m_waferCodoped = wx.Choice( self.m_hardwarePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_waferCodopedChoices, 0 )		self.m_waferCodoped.SetSelection( 0 )		fgSizer6.Add( self.m_waferCodoped, 0, wx.ALL, 5 )				self.m_staticText22 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Na", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText22.Wrap( -1 )		fgSizer6.Add( self.m_staticText22, 0, wx.ALL, 5 )				self.m_waferNA = wx.TextCtrl( self.m_hardwarePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_waferNA, 0, wx.ALL, 5 )				self.m_staticText23 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Nd", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText23.Wrap( -1 )		fgSizer6.Add( self.m_staticText23, 0, wx.ALL, 5 )				self.m_waferND = wx.TextCtrl( self.m_hardwarePanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer6.Add( self.m_waferND, 0, wx.ALL, 5 )				bSizer22 = wx.BoxSizer( wx.HORIZONTAL )				self.m_staticText21 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"Diffused", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText21.Wrap( -1 )		bSizer22.Add( self.m_staticText21, 0, wx.ALL, 5 )				m_waferDiffusedChoices = []		self.m_waferDiffused = wx.Choice( self.m_hardwarePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_waferDiffusedChoices, 0 )		self.m_waferDiffused.SetSelection( 0 )		bSizer22.Add( self.m_waferDiffused, 0, wx.ALL, 5 )				fgSizer6.Add( bSizer22, 1, wx.EXPAND, 5 )				bSizer35 = wx.BoxSizer( wx.HORIZONTAL )				self.m_staticText24 = wx.StaticText( self.m_hardwarePanel, wx.ID_ANY, u"# of Sides", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText24.Wrap( -1 )		bSizer35.Add( self.m_staticText24, 0, wx.ALL, 5 )				m_waferNumSidesChoices = []		self.m_waferNumSides = wx.Choice( self.m_hardwarePanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_waferNumSidesChoices, 0 )		self.m_waferNumSides.SetSelection( 0 )		bSizer35.Add( self.m_waferNumSides, 0, wx.ALL, 5 )				fgSizer6.Add( bSizer35, 1, wx.EXPAND, 5 )				sbSizer1.Add( fgSizer6, 1, wx.EXPAND, 5 )				fgSizer7.Add( sbSizer1, 1, wx.EXPAND, 5 )				fgSizer8 = wx.FlexGridSizer( 2, 2, 0, 0 )		fgSizer8.SetFlexibleDirection( wx.BOTH )		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )				self.m_dataOutputDir = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Data output directory", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer8.Add( self.m_dataOutputDir, 0, wx.ALL, 5 )				fgSizer7.Add( fgSizer8, 1, wx.EXPAND, 5 )				self.m_button12 = wx.Button( self.m_hardwarePanel, wx.ID_ANY, u"Perform Measurement", wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer7.Add( self.m_button12, 0, wx.ALL, 5 )				bSizer3.Add( fgSizer7, 1, wx.EXPAND, 5 )				self.m_hardwarePanel.SetSizer( bSizer3 )		self.m_hardwarePanel.Layout()		bSizer3.Fit( self.m_hardwarePanel )		self.m_notebook1.AddPage( self.m_hardwarePanel, u"Hardware Settings", False )		self.m_measurementSettingsPanel = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )		bSizer19 = wx.BoxSizer( wx.VERTICAL )				fgSizer1 = wx.FlexGridSizer( 2, 4, 0, 0 )		fgSizer1.SetFlexibleDirection( wx.BOTH )		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )						fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )				self.m_staticText2 = wx.StaticText( self.m_measurementSettingsPanel, wx.ID_ANY, u"Start Temp", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText2.Wrap( -1 )		fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )				self.m_staticText3 = wx.StaticText( self.m_measurementSettingsPanel, wx.ID_ANY, u"End Temp", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText3.Wrap( -1 )		fgSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )				self.m_staticText4 = wx.StaticText( self.m_measurementSettingsPanel, wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText4.Wrap( -1 )		fgSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )				self.m_staticText1 = wx.StaticText( self.m_measurementSettingsPanel, wx.ID_ANY, u"Temperature", wx.DefaultPosition, wx.DefaultSize, 0 )		self.m_staticText1.Wrap( -1 )		fgSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )				self.m_startTemp = wx.TextCtrl( self.m_measurementSettingsPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_startTemp, 0, wx.ALL, 5 )				self.m_endTemp = wx.TextCtrl( self.m_measurementSettingsPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_endTemp, 0, wx.ALL, 5 )				self.m_stepTemp = wx.TextCtrl( self.m_measurementSettingsPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )		fgSizer1.Add( self.m_stepTemp, 0, wx.ALL, 5 )				bSizer19.Add( fgSizer1, 1, wx.EXPAND, 5 )				self.m_autoPanel = wx.Panel( self.m_measurementSettingsPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )		bSizer19.Add( self.m_autoPanel, 1, wx.EXPAND |wx.ALL, 5 )				bSizer18 = wx.BoxSizer( wx.HORIZONTAL )				self.m_save = wx.Button( self.m_measurementSettingsPanel, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer18.Add( self.m_save, 0, wx.ALL|wx.EXPAND, 5 )				self.m_load = wx.Button( self.m_measurementSettingsPanel, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer18.Add( self.m_load, 0, wx.ALL|wx.EXPAND, 5 )				self.m_upload = wx.Button( self.m_measurementSettingsPanel, wx.ID_ANY, u"Upload", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer18.Add( self.m_upload, 0, wx.ALL|wx.EXPAND, 5 )				self.m_display = wx.Button( self.m_measurementSettingsPanel, wx.ID_ANY, u"Display", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer18.Add( self.m_display, 0, wx.ALL|wx.EXPAND, 5 )				self.m_performMeasurement = wx.Button( self.m_measurementSettingsPanel, wx.ID_ANY, u"Perform Measurments", wx.DefaultPosition, wx.DefaultSize, 0 )		bSizer18.Add( self.m_performMeasurement, 0, wx.ALL|wx.EXPAND, 5 )				bSizer19.Add( bSizer18, 1, wx.EXPAND, 5 )				self.m_measurementSettingsPanel.SetSizer( bSizer19 )		self.m_measurementSettingsPanel.Layout()		bSizer19.Fit( self.m_measurementSettingsPanel )		self.m_notebook1.AddPage( self.m_measurementSettingsPanel, u"Measurement Settings", False )				main_hbox.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )				self.SetSizer( main_hbox )		self.Layout()				self.Centre( wx.BOTH )		def __del__( self ):		pass	