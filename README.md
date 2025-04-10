
# korad power supply codes

These codes were tested with a Korad KWR102, connected via USB to a laptop running Ubuntu.  It was later updated to work for the 4-ch Korad KC3405, probably breaking 
what worked for KWR102.

Author: Blair Jamieson (2025)

## kontrol_korad.py

This is the control code that could be imported as a module.  It has one main class '''KoradPowerSupply''' which you supply the device port (/dev/ttyUSB0 for example, or whatever device name is needed) and the list of channel numbers. 

## korad_tk_gui.py

This is a GUI for the four channel Korad KC3405 that includes buttons to set the voltage, current, and power on and off the channels.

