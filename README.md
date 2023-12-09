# solis-multiplexer

The Solis wifi datalogger communicates with the monitored inverter over RS485+modbus. 
DIY interaction with the inverter over RS485 requires one of:
 * disconnecting the datalogger entirely
 * sharing the connection and accepting that sometimes there will be traffic collisions and data corruption
 * using some form of abritration to prevent collisions.

This document describes how to do the third option using a Raspberry Pi interposed between datalogger and inverter.

## Operating Principle

The wifi datalogger is connected to the Pi over a dedicated RS485 link. In turn the Pi has is own link to the inverter.
Software running on the Pi forwards traffic from the datalogger to the inverter and back. 
The Pi can also originate messages to the inverter, which will not be seen by the datalogger.
If both the datalogger and the Pi try to communicate at the same time, one will be delayed until the other has completed.

![Picture of Pi cabling](/passthrough.png)

## Bill of Materials

 * 1x A Raspberry Pi (I used a 4B)
 * 2x CH340 USB->RS485 adapters (eg https://www.amazon.co.uk/YOUMILE-CH340-Converter-Adapter-Module/dp/B07TYMWNV5 )
 * Some length of twisted pair cable (eg an ethernet cable)
 * 1x Exceedconn EC04681-2023-BF male/female pair (eg https://www.ebay.co.uk/itm/195668989940 )
 * 1x 120 Ohm resistor (eg https://www.amazon.co.uk/Watt-Carbon-Film-Resistor-Tolerance/dp/B0917XCBNL )

## Tools

 * Soldering Iron
 * Solder
 * Wire cutters, strippers
 * Drill+spade bit for male Exceedcon mounting hole (optional)
 * Small flat-head electrical screwdriver


## Steps

 * Decide where the Pi will live, and where the datalogger will be mounted. eg, mounted inside a DIN equipment box. The datalogger will be mounted on the male Exceedcon connector. Ideally this is panel mounted, requiring a drilled mounting hole.
 * Cut /in a single length/ sufficient twisted pair cable to run from the inverter serial port to the Pi and then to the datalogger mount. If practical, run the cable now and perform the remainder of the assembly in situ.
 * Prepare a mounting hole for the Male Exceedconn connector.
 * At the point at which the cable reaches the Pi, split the cable sheath and extract the orange pair. If the Pi and datalogger are close, it may be preferable to strip all the way from the datalogger end to the Pi.
 * At each end of the cable, strip the orange and green pairs. The remaining pairs are unused and can be trimmed.
 * Cut and strip the orange pair by the Pi.
 * Solder the following connections at each end of the cable. Male Exceedconn at the datalogger end, Female at the inverter end.
   * Green: Pin 1   (+5V)
   * Green+White: Pin 2 (Ground)
   * Orange: Pin 3 (D+)
   * Orange+White: Pin 4 (D-)
 * At the interior cuts on the orange pair, solder on pins (use trimmings from the resistor legs)
 * Connect each pair to one of the RS485-USB adapters, Using:
   * Orange: D+
   * Orange-white: D-
   On the RS485 adapter facing the datalogger, bridge a 120 ohm resister between the D+ and D- ports.
 * Plug the RS485 adapters into the powered Pi. Make a note of the device names for each adapter(check the output of `dmesg`). They will be of the form `/dev/ttyUSBx`. It's important to know which faces the inverter and which the datalogger.
 * Plug in the cable to the inverter
 * Plug in the datalogger to the male Exceedcon 


## Software

 * On the Pi, run `passthrough /dev/ttyUSBx /dev/ttyUSBy` where `ttyUSBx` is that of the datalogger and `ttyUSB1` is that of the inverter.
   This will log the data sent between datalogger and inverter.
 * To send commands to the inverter, the relevant tty must be locked using `flock`. For example, to read the inverter state:
```
flock -w 5 -x /dev/ttyUSBy  ./inverter_control.py
```

Will block for at most 5 seconds, waiting until there is no communication between the datalogger and inverter.

