import wx


from gui.new_gui import IncrementalApp
from gui.Validator import NumRangeValidator

from util.Constants import WAVEFORMS, OUTPUTS
from util.Exceptions import PVInputError

known_types = {
    'int': int,
    'float': float,
    'str': str,
    'bool': bool
}


class Form(object):
    """A collection of related input widgets"""

    def __init__(self, name, widget_list):
        self.name = name
        self.widget_list = widget_list


class FormElement(object):
    """docstring for FormElement"""
    def __init__(self, widget, widget_id, input_type):
        self.widget = widget
        self.widget_id = widget_id
        self.input_type = input_type


class View1(IncrementalApp):
    def __init__(self, parent):
        IncrementalApp.__init__(self, parent)

        self.data_file = None

        # hardware layout
        self._pl_calibration_labels = [
            "None",
            "Self-consistent",
            "Nan's method",
            "Match PL to PC",
            "Other"
        ]
        self._yes_no_labels = [
            "No",
            "Yes"
        ]

        self._num_sides_labels = [
            "1 side",
            "2 sides"
        ]
        self._set_hardware_dropdowns()

        # experiment settings layout
        self.input_rows = []
        column_titles_str = [
            u"", u"Waveform", u"Period", u"Amplitude", u"Offset1",
            u"Offset2", u"Sample Rate", u"LED state", u"Filter", u"Binning"
        ]

        self._experiment_form = []

        self.NUM_ROWS = 4

        for row_index in xrange(self.NUM_ROWS):
            self._experiment_form.append(
                Form(
                    name="Experiment " + str(row_index),
                    widget_list=[
                        FormElement(None, "waveform", "str"),
                        FormElement(None, "duration", "float"),
                        FormElement(None, "amplitude", "float"),
                        FormElement(None, "offset_before", "int"),
                        FormElement(None, "offset_after", "int"),
                        FormElement(None, "sample_rate", "float"),
                        FormElement(None, "channel", "str"),
                        FormElement(None, "binning", "int"),
                        FormElement(None, "averaging", "int")
                    ]
                )
            )

        self._wafer_form = Form(
            name="Wafer",
            widget_list=[
                FormElement(self.m_waferID, "wafer_id", "str"),
                FormElement(self.m_waferThickness, "wafer_thickness", "float"),
                FormElement(self.m_waferCodoped, "wafer_codoped", "bool"),
                FormElement(self.m_waferNA, "wafer_na", "float"),
                FormElement(self.m_waferND, "wafer_nd", "float"),
                FormElement(self.m_waferDiffused, "wafer_diffused", "bool"),
                FormElement(self.m_waferNumSides, "wafer_num_sides", "str")
            ]
        )

        self._temperature_form = Form(
            name="Temperature",
            widget_list=[
                FormElement(self.m_startTemp, "start_temp", "int"),
                FormElement(self.m_endTemp, "end_temp", "int"),
                FormElement(self.m_stepTemp, "step_temp", "int")
            ],
        )

        # setup flexible grid sizer for form construction
        self.fgSizerAuto = wx.FlexGridSizer(self.NUM_ROWS + 1, 10, 0, 0)
        self.fgSizerAuto.SetFlexibleDirection(wx.BOTH)
        self.fgSizerAuto.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        for title in column_titles_str:
            self._add_title_row(title)

        for num in range(self.NUM_ROWS):
            self.input_rows.append(self._add_row(num + 1))

            for index, widget in enumerate(self.input_rows[num][1:]):
                self._experiment_form[num].widget_list[index].widget = widget

        self.m_autoPanel.SetSizer(self.fgSizerAuto)
        self.m_autoPanel.Layout()
        # self.fgSizerAuto.Fit(self.m_autoPanel)

        self.Layout()

        self._set_ui_validators()
        self._bind_checkbox_disable()

        # self._test_setters()

    def _test_setters(self):
        self.set_temperature_form({
            "start_temp": 1,
            "end_temp": 5,
            "step_temp": 1
        })

        self.set_wafer_form({
            "wafer_id": "wafer1",
            "wafer_thickness": 33.0,
            "wafer_codoped": True,
            "wafer_na": 1,
            "wafer_nd": 6,
            "wafer_diffused": True,
            "wafer_num_sides": 1
        })

        self.set_experiment_form([
            {
                "waveform": 0,
                "duration": 1,
                "amplitude": 0.5,
                "offset_before": 1,
                "offset_after": 10,
                "sample_rate": 1.2e3,
                "channel": 0,
                "binning": 1,
                "averaging": 1,
            },
            {
                "waveform": 1,
                "duration": 1,
                "amplitude": 0.5,
                "offset_before": 1,
                "offset_after": 10,
                "sample_rate": 1.2e3,
                "channel": 1,
                "binning": 1,
                "averaging": 5,
            }
        ])

    def get_form(self, form, allow_incomplete):
        typed_inputs = {}

        for entry in form.widget_list:
            try:
                type_func = known_types[entry.input_type]
                if isinstance(entry.widget, wx.Choice):
                    typed_inputs[entry.widget_id] = int(
                        entry.widget.GetSelection()
                    )
                else:
                    typed_inputs[entry.widget_id] = type_func(
                        entry.widget.GetValue()
                    )
            except ValueError as e:
                print entry.widget_id, entry.widget.GetValue()
                print("ERROR", e)
                if not allow_incomplete and entry.widget.GetValue() == '':
                    raise PVInputError("No value for {0} in form {1}".format(
                        entry.widget_id, form.name
                    ))
        return typed_inputs

    def get_temperature_form(self, allow_incomplete=False):
        return self.get_form(self._temperature_form, allow_incomplete)

    def get_wafer_form(self, allow_incomplete=False):
        return self.get_form(self._wafer_form, allow_incomplete)

    def get_experiment_form(self, allow_incomplete=False):
        inputs = []
        for row, experiment in enumerate(self._experiment_form):

            # check if the row is enabled.
            if self.input_rows[row][0].GetValue() is True:
                inputs.append(self.get_form(experiment, allow_incomplete))
        return inputs

    def set_wafer_form(self, wafer_settings):
        for element in self._wafer_form.widget_list:
            widget = element.widget
            print("wafer settings: ", wafer_settings)
            value = wafer_settings[element.widget_id]
            if isinstance(widget, wx.Choice):
                widget.SetSelection(value)
            else:
                widget.SetValue(str(value))

    def set_temperature_form(self, temp_settings):
        for element in self._temperature_form.widget_list:
            element.widget.SetValue(str(temp_settings[element.widget_id]))

    def set_experiment_form(self, experiment_settings):
        for row_num in range(self.NUM_ROWS):
            for element in self._experiment_form[row_num].widget_list:
                try:
                    value = experiment_settings[row_num][element.widget_id]
                    if isinstance(element.widget, wx.Choice):
                        element.widget.SetSelection(value)
                    else:
                        element.widget.SetValue(str(value))
                except Exception as e:
                    print("Experiment Error: ", e)
                    pass

    def clear_experiment_form(self):
        for row_num in range(self.NUM_ROWS):
            for element in self._experiment_form[row_num].widget_list:
                try:
                    if isinstance(element.widget, wx.Choice):
                        element.widget.SetSelection(0)
                    else:
                        element.widget.SetValue("")
                except Exception as e:
                    print("Experiment Error: ", e)

    def disable_all_settings_inputs(self):
        for row in self.input_rows:
            self._disable_row(row)

    def show_calibration_modal(self):
        msg_text = (
            "Please remove sample from measurement area\n"
            "Only one PC calibration is necessary per experimental session"
        )
        wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)

    def show_info_modal(self, message_text):
        wx.MessageBox(message_text, 'Info', wx.OK | wx.ICON_INFORMATION)

    def show_error_modal(self, message_text):
        wx.MessageBox(message_text, 'Error', wx.OK | wx.ICON_ERROR)

    def ask_user_for_filename(self, **dialog_options):
        print(dialog_options)
        dialog = wx.FileDialog(self, **dialog_options)
        path_parameters = None, None
        if dialog.ShowModal() == wx.ID_OK:
            path_parameters = dialog.GetFilename(), dialog.GetDirectory()
        dialog.Destroy()
        return path_parameters

    def ask_user_for_dir(self, **dialog_options):
        dialog = wx.DirDialog(self, **dialog_options)

        path_parameters = None, None
        if dialog.ShowModal() == wx.ID_OK:
            path_parameters = dialog.GetPath()
        dialog.Destroy()
        return path_parameters

    def _bind_checkbox_disable(self):
        for row in self.input_rows:
            row[0].Bind(
                wx.EVT_CHECKBOX,
                self._disable_part_row
            )

    def _disable_part_row(self, event):
        sender = event.GetEventObject()

        checkbox_list = [row[0] for row in self.input_rows]
        row_num = checkbox_list.index(sender)

        is_checked = sender.GetValue()

        if is_checked:
            self._enable_row(self.input_rows[row_num], start_element=1)
        else:
            self._disable_row(self.input_rows[row_num], start_element=1)

    def _disable_row(self, row, start_element=0):
        for index, element in enumerate(row):
            if index >= start_element:
                element.Disable()

    def _enable_row(self, row, start_element=0):
        for index, element in enumerate(row):
            if index >= start_element:
                element.Enable()

    def _set_hardware_dropdowns(self):
        self.m_plCalibrationMethod.SetItems(self._pl_calibration_labels)
        self.m_waferCodoped.SetItems(self._yes_no_labels)
        self.m_waferDiffused.SetItems(self._yes_no_labels)
        self.m_waferNumSides.SetItems(self._num_sides_labels)

    def _add_row(self, number):
        row_elements = []
        row_elements.append(self._add_checkbox(unicode(number)))
        row_elements.append(self._add_dropdown(WAVEFORMS))
        for i in range(5):
            row_elements.append(self._add_textctrl())
        row_elements.append(self._add_dropdown(OUTPUTS))
        for i in range(2):
            row_elements.append(self._add_textctrl())
        return row_elements

    def _add_title_row(self, row_title):
        row = wx.StaticText(
            self.m_autoPanel, wx.ID_ANY, row_title,
            wx.DefaultPosition, wx.DefaultSize, 0
        )
        row.Wrap(-1)
        self.fgSizerAuto.Add(row, 0, wx.ALL, 5)
        return row

    def _add_checkbox(self, number):
        checkbox = wx.CheckBox(
            self.m_autoPanel, wx.ID_ANY, number, wx.DefaultPosition,
            wx.DefaultSize, 0
        )
        checkbox.SetValue(True)
        self.fgSizerAuto.Add(checkbox, 0, wx.ALL, 5)
        return checkbox

    def _add_textctrl(self):
        text_ctrl = wx.TextCtrl(
            self.m_autoPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, 0
        )
        text_ctrl.SetMaxSize(wx.Size(50, -1))
        self.fgSizerAuto.Add(text_ctrl, 0, wx.ALL, 5)
        return text_ctrl

    def _add_dropdown(self, options):
        dropdown = wx.Choice(
            self.m_autoPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            options, 0
        )
        dropdown.SetSelection(0)
        self.fgSizerAuto.Add(dropdown, 0, wx.ALL, 5)
        return dropdown

    def _set_ui_validators(self):
        for element in self._temperature_form.widget_list:
            element.widget.SetValidator(
                NumRangeValidator(numeric_type=element.input_type)
            )

        for element in self._wafer_form.widget_list:
            if element.input_type in ["int", "float"]:
                element.widget.SetValidator(
                    NumRangeValidator(numeric_type=element.input_type)
                )

        for row in self._experiment_form:
            for element in row.widget_list:
                if element.input_type in ["int", "float"]:
                    element.widget.SetValidator(
                        NumRangeValidator(numeric_type=element.input_type)
                    )
