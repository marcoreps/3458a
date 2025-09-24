#!/usr/bin/env python
# -*- coding: utf-8 -*-
# developed & tested with Python 3.9

from time import sleep
from datetime import datetime, timedelta, timezone
import pyvisa
rm = pyvisa.ResourceManager()

import atexit
from multiprocessing import Process, Queue

measurement_filename = "hedrix_preamp_3458b_1nplc.csv"


def setup_dmm():
    inst =  rm.open_resource('TCPIP::192.168.0.5::gpib0,23')
    inst.clear()
    inst.write("PRESET FAST")
    inst.write("END ALWAYS")
    inst.write("ARANGE OFF")
    inst.write("DISP OFF")              # Disable Diplay
    inst.write("MATH OFF")
    inst.write("MEM OFF")
    inst.write("OFORMAT DINT")          # SINT, ASCII
    inst.write("DEFEAT ON")
    inst.write("LOCK ON")               # Local lock
    inst.write("DCV 10")
    inst.write("NPLC 1")
    #inst.write("APER 1.4E-6")
    inst.write("AZERO 0")
    inst.write("TARM HOLD")
    inst.write("NRDGS 1,AUTO")
    inst.write("TRIG AUTO")
    inst.write("DELAY 0")
    return inst

def run_measurement(inst, filename, scale, queue, finish):
    while not finish:
        data = inst.read_raw()
        test_time = datetime.now(timezone.utc).astimezone()
        queue.put(f"{test_time.isoformat()}\t{int.from_bytes(data, byteorder='big', signed=True) * scale:.6e}\n")

def write_data(value, filename, finish):
#    with open(filename, 'a') as file_handle:        # append
    with open(filename, 'w') as file_handle:        # overwrite
        while not finish:
            while not value.empty():
                file_handle.write(value.get())
            sleep(0.01)

def exit_handler(inst, finish, write_process, measurement):
    finish = True                                   # stop processes
    inst.clear()						            # needed to exit fast mode
    inst.write("DISP MSG,\"                 \"")    # enable Display and empty
    inst.write("LOCK OFF")                          # local lock disable
    while write_process.is_alive() or measurement.is_alive():
        print("Waiting for processes to end...")
        sleep(0.01)
    print('Despite the errors: exited gracefully')

def main():
    global measurement_filename
    
    data = Queue()                                  # multiprocessing queue for data
    finish = False                                  # process shared variable
    dmm = setup_dmm()

    write_process = Process(target=write_data, args=(data, measurement_filename, finish))
    write_process.start()

    dmm.write("ISCALE?")
    scale = float(dmm.read_raw().strip().decode('utf-8'))
    dmm.write("TARM AUTO")

    print (f"Collect Data DMM to \"{measurement_filename}\"")

    measurement = Process(target=run_measurement, args=(dmm, measurement_filename, scale, data, finish))
    measurement.start()

    atexit.register(exit_handler, dmm, finish, write_process, measurement)	# graceful exit no matter what

    print("Measurement running... finish with CTRL-C")
    measurement.join()
        
    print("Done with measurements")

if __name__ == "__main__":
    main()
