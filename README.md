# UI - Readme

This to contain instructions a non-developer end user could use to get this running.

# LICENCE

Decide on later.

# Dev setup.

## Install dependencies.
The order matter.
* Windows 7 (or later)
* Python XY (which version)
* wxPython (which version?)
* Microsoft .NET Framework 4.5
* Labview 2013 64bit (or later)
* NI-DAQmx (make sure it's > 14.5)
* Git

Why python(x,y)? Apparently a common motivation is to get around the need to have pip access a compiler when installing requirements.txt files.

If not using python(x,y) then things are more complicated:

wxpython distribution

Microsoft Visual C++ Compiler for Python 2.7
http://www.microsoft.com/en-au/download/details.aspx?id=44266

See stackoverflow answer here to get wxpython playing with virtualenv:
http://stackoverflow.com/questions/7139749/how-to-install-wxpython-using-virtualenv

    The solution I ended up using was to install python to my main system:

    Then make a symbolic link from the wx in my system python to my virtual environment:

    ln -s /usr/lib/python2.7/dist-packages/wxversion.py <virtual_env_path>/lib/python2.7/site-packages/wxversion.py

    Where is the path in my case to a virtual environment named "fibersim" for example is:
    /home/adam/anaconda/envs/fibersim


## Set up a simulated device for testing.
![How to setup a simulated device](/doc/configuring_test_device.gif)

Then run main.py

## Workflow

We'll use "master" for the current state of development, but new features should be taken to new branches then merged to master when working.

"master" won't be necessarily releasable. Releases will be tagged.
