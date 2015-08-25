import wx
import sys
from util import utils

MAX_LOCALE_CHAR = 256


class NumRangeValidator(wx.PyValidator):
    """
    Numeric Validator for a TextCtrl
    """

    def __init__(self, numeric_type='int', min_=0, max_=sys.maxint):
        super(NumRangeValidator, self).__init__()

        if numeric_type == 'int':
            assert min_ >= 0
        self._min = min_
        self._max = max_
        self.numeric_type = numeric_type
        if numeric_type == 'int':
            self.convert_to_num = int
            self.allow_chars = "-1234567890"
            self.is_num = lambda x: x.isdigit()
        elif numeric_type == 'float':
            self.convert_to_num = float
            self.allow_chars = "+-.e1234567890"
            self.is_num = utils.is_float

        # Event management
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """Require override"""
        return NumRangeValidator(self.numeric_type, self._min, self._max)

    def Validate(self, win):
        """
        Override to validate window's value
        Return: Boolean
        """
        txtCtrl = self.GetWindow()
        val = txtCtrl.GetValue()
        isValid = False
        if self.is_num(val):
            digit = self.convert_to_num(val)
            if digit >= self._min and digit <= self._max:
                isValid = True

        if not isValid:
            message = 'Data must be {0} between {1} and {2}'.format(
                self.numeric_type,
                self._min,
                self._max
            )
            pub.sendMessage(
                'statusbar.update',
                message,
                error=True
            )
            return isValid

    def OnChar(self, event):
        txtCtrl = self.GetWindow()
        key = event.GetKeyCode()
        isDigit = False
        if key < 256:
            isValid = chr(key) in self.allow_chars
        if key in (wx.WXK_RETURN, wx.WXK_DELETE, wx.WXK_BACK) or key > 255 or isValid:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            # Beep to warn about invalid input
            wx.Bell()
        return

    def TransferToWindow(self):
        """Overridden to skip data transfer"""
        return True

    def TransferFromWindow(self):
        """Overridden to skip data transfer"""
        return True
