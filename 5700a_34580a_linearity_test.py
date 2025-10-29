#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
from datetime import datetime
import time
import numpy as np
import random
import logging

timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
measurement_filename = "INL/3458A_34470A_10V_INL_"+timestr+".csv"
voltage_min = -10
voltage_max = 10
random_voltage_offset_range = 1.0
n_test_points = 20
NPLC = 10
n_measurements_per_meter_per_point = 10

instruments = dict()
rm = pyvisa.ResourceManager()

def setup_3458a(addr):
    inst = rm.open_resource(addr)
    inst.clear()
    inst.write("RESET")
    inst.write("END ALWAYS")
    inst.write("OFORMAT ASCII")
    inst.write("BEEP")
    inst.write("DCV 10")
    inst.write("NPLC "+str(NPLC))
    inst.write("TARM HOLD")
    logging.info("ID? -> "+inst.query("ID?"))
    return inst
    
def setup_34470a(addr):
    inst = rm.open_resource(addr)
    inst.clear()
    inst.write("*RST")
    inst.write("*CLS")
    inst.write("CONF:VOLT:DC 10")
    inst.write("SENS:VOLT:DC:NPLC "+str(NPLC))
    inst.write("SENS:VOLT:DC:AZERO ON")
    inst.write("TRIG:SOURce AUTO")
    inst.write("TRIG:COUN INF")
    inst.write("SAMP:COUN 1")
    logging.info("ID? -> "+inst.query("*IDN?"))
    return inst
    
def setup_5700a(addr):
    inst = rm.open_resource(addr)
    inst.clear()
    inst.write("*RST")
    inst.write("*CLS")
    inst.write("STBY") 
    inst.write("OUT 0.0 V, 0 Hz")
    inst.write("OPER")
    logging.info("ID? -> "+inst.query("*IDN?"))
    return inst
    
def one_sweep(instruments, source):
    test_points = np.linspace(voltage_min, voltage_max, n_test_points)
    test_points += random.uniform(random_voltage_offset_range*-0.5, random_voltage_offset_range*0.5)
    logging.info(f"Todays lucky numbers are:\n{test_points}")
    
instruments["3458B"]=setup_3458a('TCPIP::192.168.0.5::gpib0,23')
instruments["3458P"]=setup_3458a('TCPIP::192.168.0.5::gpib0,22')
instruments["3458H"]=setup_3458a('gpib0::21::INSTR')
instruments['3458A_MY45054264']=setup_3458a('gpib0::2::INSTR')
instruments['3458A_US28028957']=setup_3458a('gpib0::24::INSTR')
instruments['3458A_MY59352556']=setup_3458a('gpib0::22::INSTR')
instruments['3458A_2823A25425']=setup_3458a('gpib0::5::INSTR')
instruments['34470A']=setup_34470a('TCPIP::192.168.0.103::inst0::INSTR')
source=setup_5700a('GPIB0::1::INSTR')

one_sweep(instruments, source)