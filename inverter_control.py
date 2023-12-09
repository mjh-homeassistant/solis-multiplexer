#!/usr/bin/env python3

import minimalmodbus
import time
import os
import sys
import fcntl
import json

def get_status():
    status={}
    # Inverter Temp
    inverter_temp = instrument.read_register(33093, functioncode=4, number_of_decimals=1, signed=False)
    status["inverter_temp"]=inverter_temp
    # Inverter Time
    inverter_time_hour = instrument.read_register(33025, functioncode=4, signed=False)
    status["inverter_time_hour"]=inverter_time_hour
    inverter_time_min = instrument.read_register(33026, functioncode=4, signed=False)
    status["inverter_time_min"]=inverter_time_min
    inverter_time_sec = instrument.read_register(33027, functioncode=4, signed=False)
    status["inverter_time_sec"]=inverter_time_sec

    # Battery Status, 0=Charge, 1=Discharge
    battery_status = instrument.read_register(33135, functioncode=4, signed=False)
    status["battery_status"]=battery_status

    # Battery SOC
    battery_soc = instrument.read_register(33139, functioncode=4, signed=False)
    status["battery_soc"]=battery_soc

    # Battery SOH
    battery_soh = instrument.read_register(33140, functioncode=4, signed=False)
    status["battery_soh"]=battery_soh

    # Grid Power (w), Positive=Export, Negative=Import
    grid_power = instrument.read_long(33130, functioncode=4, signed=True)
    status["grid_power"]=grid_power

    # House load power (w)
    house_power = instrument.read_register(33147, functioncode=4, signed=False)
    status["house_power"]=house_power

    # Battery Power (w)
    battery_power = instrument.read_long(33149, functioncode=4, signed=True)
    status["battery_power"]=battery_power

    # Current generation (Active power) (w), need to confirm when generating
    current_generation =  instrument.read_long(33057, functioncode=4, signed=False)
    status["current_generation"]=current_generation
    total_active_power =  instrument.read_long(33263, functioncode=4, signed=True)
    status["total_active_power"]=total_active_power
    # instrument.read_long(33079, functioncode=4, signed=True)
    # possibly this too 33263? "Meter total active power"

    # Total generation today (kWh)
    generation_today = instrument.read_register(33035, functioncode=4, number_of_decimals=1, signed=False)
    status["generation_today"]=generation_today

    # Total generation yesterday (kWh)
    generation_yesterday = instrument.read_register(33036, functioncode=4, number_of_decimals=1, signed=False)

    # Battery storage mode, 33=self use, 35=timed charge
    storage_mode = instrument.read_register(43110, functioncode=3, signed=False)
    status["storage_mode"]=storage_mode

    charge_current    = instrument.read_register(43141, functioncode=3, signed=False)
    status["charge_current"] = charge_current

    discharge_current = instrument.read_register(43142, functioncode=3, signed=False)
    status["discharge_current"] = discharge_current

    charge_start_hour = instrument.read_register(43143, functioncode=3, signed=False)
    status["charge_start_hour"] = charge_start_hour
    # Minute
    charge_start_min = instrument.read_register(43144, functioncode=3, signed=False)
    status["charge_start_min"] = charge_start_min
    # Timed charge end
    # Hour
    charge_end_hour = instrument.read_register(43145, functioncode=3, signed=False)
    status["charge_end_hour"] = charge_end_hour
    # Minute
    charge_end_min = instrument.read_register(43146, functioncode=3, signed=False)
    status["charge_end_min"] = charge_end_min
    # Timed discharge start
    # Hour
    discharge_start_hour = instrument.read_register(43147, functioncode=3, signed=False)
    status["discharge_start_hour"] = discharge_start_hour
    # Minute
    discharge_start_min = instrument.read_register(43148, functioncode=3, signed=False)
    status["discharge_start_min"] = discharge_start_min
    # Timed discharge end
    # Hour
    discharge_end_hour = instrument.read_register(43149, functioncode=3, signed=False)
    status["discharge_end_hour"] = discharge_end_hour
    # Minute
    discharge_end_min = instrument.read_register(43150, functioncode=3, signed=False)
    status["discharge_end_min"] = discharge_end_min


    print(json.dumps(status, indent=2, sort_keys=True))


def timed_charge():
    # We can use read_registers to grab all the values in one call:
    # instrument.read_registers(43143, number_of_registers=8, functioncode=3)
    # Not going to check charge/discharge for now, we haven't implemented it yet.
    # Timed charge start
    # Hour
    charge_current    = instrument.read_register(43141, functioncode=3, signed=False)
    discharge_current = instrument.read_register(43142, functioncode=3, signed=False)
    charge_start_hour = instrument.read_register(43143, functioncode=3, signed=False)
    # Minute
    charge_start_min = instrument.read_register(43144, functioncode=3, signed=False)
    # Timed charge end
    # Hour
    charge_end_hour = instrument.read_register(43145, functioncode=3, signed=False)
    # Minute
    charge_end_min = instrument.read_register(43146, functioncode=3, signed=False)
    # Timed discharge start
    # Hour
    discharge_start_hour = instrument.read_register(43147, functioncode=3, signed=False)
    # Minute
    discharge_start_min = instrument.read_register(43148, functioncode=3, signed=False)
    # Timed discharge end
    # Hour
    discharge_end_hour = instrument.read_register(43149, functioncode=3, signed=False)
    # Minute
    discharge_end_min = instrument.read_register(43150, functioncode=3, signed=False)
    print(f"Charge current {charge_current/10}A")
    print(f"Discharge current {charge_current/10}A")
    print(f"Charge Start: {charge_start_hour}:{charge_start_min}")
    print(f"Charge End: {charge_end_hour}:{charge_end_min}")
    print(f"Discharge Start: {discharge_start_hour}:{discharge_start_min}")
    print(f"Discharge End: {discharge_end_hour}:{discharge_end_min}")

    # Change charge start time minute, will work the same for the othe values.
    # instrument.write_register(43144, functioncode=6, signed=False, value=54)
    # We can write all the times in one call with write_registers:
    # instrument.write_registers(43143, [10, 11, 12, 13, 14, 15, 16, 17])

    # instrument.write_registers(43143, [3, 00, 6, 00, 00, 00 ,00 ,00 ])


if __name__ == "__main__":
   port = sys.argv[1]
   fd=os.open(port, os.O_RDONLY)
   fcntl.flock(fd, fcntl.LOCK_EX)

    
   instrument = minimalmodbus.Instrument(port, 1, debug = False)
   instrument.serial.baudrate = 9600
   instrument.serial.timeout = 2

   get_status()
   os.close(fd)

