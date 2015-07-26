ToDo
######

* describe setup for build environment
* remove wildcard imports
* remove hardcoded filepaths
* reorganize code in Main_V0.1.py into proper modules
* reorganize classes so DRY and SRP
* get sphinx documentation working
* write unit tests for existing classes
* document existing methods
* write wrappers for the follow dll functions

    nidaq.DAQmxCreateTask
    nidaq.DAQmxStartTask
    nidaq.DAQmxStopTask
    nidaq.DAQmxClearTask
    nidaq.DAQmxReadAnalogF64
    nidaq.DAQmxWriteAnalogF64
    nidaq.DAQmxGetErrorString
    nidaq.DAQmxCfgSampClkTiming
    nidaq.DAQmxCreateAIVoltageChan
    nidaq.DAQmxCreateAOVoltageChan


Done
####
2) document existing classes: little sparse, but should probably start going through the methods as well



Questions for engineers
#######################
What is frequency scan?


Add to documentation
####################
How to add wx to virtual environment

1) Install wx globally:

[matt@ockham: ~/projects/PVapp/pvapp] $ python
Python 2.7.9 (default, Feb 10 2015, 03:29:19)
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.56)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import wx
>>> wx.__file__
'/usr/local/lib/wxPython-3.0.2.0/lib/python2.7/site-packages/wx-3.0-osx_cocoa/wx/__init__.pyc'

2) add file "wx.pth" with the path to your wx package:
    /usr/local/lib/wxPython-3.0.2.0/lib/python2.7/site-packages/wx-3.0-osx_cocoa
 to:
    ~/envs/pvapp/lib/python2.7/site-packages/

NB: still doesn't work properly with matplotlib
3)
