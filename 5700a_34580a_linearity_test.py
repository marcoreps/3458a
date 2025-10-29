#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
from datetime import datetime
import time
import numpy as np
import random
import logging

filename = "INL/3458A_34470A_10V_INL_"
voltage_min = -10
voltage_max = 10
random_voltage_offset_range = 1.0
n_test_points = 20
NPLC = 10
n_measurements_per_meter_per_point = 10
soak_time = 10

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logging.info("Starting ...")

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
    inst.write("TRIG:SOURce BUS")
    inst.write("INITiate")
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
    
def measure(inst):
    reading = 0
    for n in range(n_measurements_per_meter_per_point):
        if inst['type'] == '3458A':
            reading += float(inst['inst'].query("TARM SGL"))/n_measurements_per_meter_per_point
            logging.info(f"A 3458A read {reading}")
        else:
            inst['inst'].write("*TRG")
            reading = float(inst['inst'].query("FETCH?"))/n_measurements_per_meter_per_point
            logging.info(f"A 34470A read {reading}")
    return reading
    
def one_sweep(instruments_list, source, filename):
    timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename_with_time = filename+timestr+".csv"
    test_points = np.linspace(voltage_min, voltage_max, n_test_points)
    test_points += random.uniform(random_voltage_offset_range*-0.5, random_voltage_offset_range*0.5)
    logging.info(f"Todays lucky numbers are:\n{test_points}")
    i = 0
    for v in test_points:
        source.write("OUT %.7f" % v)
        time.sleep(soak_time)
        random.shuffle(instruments_list)
        for inst in instruments_list:
            inst["results"][i]=measure(inst)
        i += 1
            
        


instruments["3458B"] = {'type': '3458A', 'inst': setup_3458a('TCPIP::192.168.0.5::gpib0,23'), "results": [0] * n_test_points}
instruments["3458P"] = {'type': '3458A', 'inst': setup_3458a('TCPIP::192.168.0.5::gpib0,22'), "results": [0] * n_test_points}
instruments["3458H"] = {'type': '3458A', 'inst': setup_3458a('gpib0::21::INSTR'), "results": [0] * n_test_points}
instruments['3458A_MY45054264'] = {'type': '3458A', 'inst': setup_3458a('gpib0::2::INSTR'), "results": [0] * n_test_points}
instruments['3458A_US28028957'] = {'type': '3458A', 'inst': setup_3458a('gpib0::24::INSTR'), "results": [0] * n_test_points}
instruments['3458A_MY59352556'] = {'type': '3458A', 'inst': setup_3458a('gpib0::22::INSTR'), "results": [0] * n_test_points}
instruments['3458A_2823A25425'] = {'type': '3458A', 'inst': setup_3458a('gpib0::5::INSTR'), "results": [0] * n_test_points}
instruments['34470A'] = {'type': '34470A', 'inst': setup_34470a('TCPIP::192.168.0.103::inst0::INSTR'), "results": [0] * n_test_points}

source = setup_5700a('GPIB0::1::INSTR')


one_sweep(list(instruments.values()), source, filename)