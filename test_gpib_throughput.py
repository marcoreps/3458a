#!/usr/bin/env python
# -*- coding: utf-8 -*-
# developed & tested with Python 3.9

from time import perf_counter_ns, sleep
import atexit
from statistics import mean, median, stdev
import pyvisa
rm = pyvisa.ResourceManager()



def setup():
    inst =  rm.open_resource('TCPIP::192.168.0.5::gpib0,23')

    inst.clear()

    inst.write("TARM HOLD")             # stop measurements
    inst.write("PRESET FAST")           # preset to fast mode, see p. 156 for high-speed mode
    inst.write("END ALWAYS")            # EOI line set true when the last byte of each reading sent (read needs end of data info)

    #inst.write("DISP OFF")              # set by PRESET FAST
    #inst.write("MATH OFF")              # set by PRESET FAST
    #inst.write("MEM OFF")               # set by PRESET FAST
    #inst.write("AZERO OFF")             # set by PRESET FAST
    #inst.write("NRDGS 1,AUTO")          # set by PRESET FAST
    #inst.write("TRIG AUTO")             # set by PRESET FAST (triggers whenever the multimeter is not busy)
    inst.write("MFORMAT SINT")			# DINT set by PRESET FAST
    inst.write("OFORMAT SINT")			# DINT set by PRESET FAST
    inst.write("DEFEAT ON")             # !!! input protection reduced (only +-100V up to 10V range allowed, +-1100V on 100V/1000V range) !!! see p. 157
    inst.write("LOCK ON")				# local lock - does nothing for speed, but prevents interruptions by use of frontpanel
    inst.write("APER 1.4E-6")			# fastest see manual p. 160
    #inst.write("NPLC 1")                # for testing throughput with NPLCs
    #inst.write("DCV 1")                 # DCV 10 set by PRESET FAST
    inst.write("ARANGE OFF")            # needed according to p. 156 for high-speed mode, really needed if set to a range?
    inst.write("DELAY 0")				# sets the delay to its minimum possible value (100 ns) - see p. 159

    return inst

def run_measurement(inst, runs=10000):
    data = []

    for _1 in range(3):                            # warmup
        value = inst.read_raw()

    start = perf_counter_ns()
    for i in range(runs):
        value = inst.read_raw()
        time_ns = perf_counter_ns()
        data.append([time_ns, value])
    stop = perf_counter_ns()
		
    return data, start, stop

def exit_handler(inst):
    inst.clear()						            # needed to exit fast mode
    inst.write("DISP ON")				            # enable diplay
    inst.write("DISP MSG,\"                 \"")    # better as DISP OFF to save display life
    inst.write("LOCK OFF")				            # local lock disable
    print('Exited gracefully')
		
def main():
    ns_to_ms = 1_000_000
    
    dmm = setup()
    atexit.register(exit_handler, dmm)
    
    print (f"Starting throughput test with DMM, this will take some time ...")
    
    dmm.write("ISCALE?")
    scale = float(dmm.read_raw().strip().decode("ascii"))

    dmm.write("TARM AUTO")                          # start measurements (always armed) - see p. 159

    sleep(1)                                        # give the DMM some time to process settings
    
    count = 10_000
    data, start, stop = run_measurement(dmm, count)
    
    delta_times = []
    
    for n, datum in enumerate(data):
        delta_time = datum[0]-data[n-1][0] if n > 0 else datum[0]-start # first delta_time is special
        print (f"{n:6.0f}: {datum[0]} > {int.from_bytes(datum[1], byteorder='big', signed=True) * scale:3.6f}V dt: {delta_time/ns_to_ms:.3f}ms")
        delta_times.append(delta_time)
        
    print(f"Scale: {scale}")
    print(  f"mean: {mean(delta_times)/ns_to_ms:.3f}ms"
            f"\nmedian: {median(delta_times)/ns_to_ms:.3f}ms"
            f"\nstdev: {stdev(delta_times)/ns_to_ms:.3f}ms"
            f"\nmin: {min(delta_times)/ns_to_ms:.3f}ms @{min(range(len(delta_times)), key=delta_times.__getitem__)}"
            f"\nmax: {max(delta_times)/ns_to_ms:.3f}ms @{max(range(len(delta_times)), key=delta_times.__getitem__)}"
            )
    print(  f"runtime: {(stop-start)/ns_to_ms:.3f}ms"
            f"\ntime per sample: {(stop-start)/ns_to_ms/count:.3f}ms/spl")

if __name__ == "__main__":
    main()