#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyvisa
import time

# --- CONFIGURATION ---
debug_mode = False   # False = write to CSV, True = test SPS
measurement_filename = "csv/3458B_fullscale_8ADRmu_10V_noise_20sps.csv"

def setup_dmm(rm):
    inst = rm.open_resource('TCPIP::192.168.0.5::gpib0,23')
    inst.clear()
    inst.write("RESET")
    inst.write("PRESET NORM")
    inst.write("END ALWAYS")
    inst.write("OFORMAT ASCII")         
    inst.write("DCV 10")
    inst.write("AZERO 1")
    inst.write("DISP OFF")
    inst.write("TIMER 0.050")           
    inst.write("NRDGS 16777215, TIMER")
    
    return inst

def main():
    rm = pyvisa.ResourceManager()
    dmm = setup_dmm(rm)

    print(f"File \"{measurement_filename}\"")
    print(f"Debug Mode: {'ON (SPS benchmark)' if debug_mode else 'OFF (Writing to csv)'}")
    print("Let the GPIB cable glow... finish with CTRL+C\n")

    sample_count = 0
    
    last_print_time = time.time()
    last_sample_count = 0

    try:
        with open(measurement_filename, 'w') as file_handle:
            while True:
                data_str = dmm.read()
                voltage = float(data_str)
                
                now = time.time()
                
                sample_count += 1
                
                if debug_mode:
                    if now - last_print_time >= 1.0:
                        sps = (sample_count - last_sample_count) / (now - last_print_time)
                        print(f"Speed: {sps:.4f} SPS | Total Samples: {sample_count} | Latest: {voltage:.8e} V", end='\r')
                        last_print_time = now
                        last_sample_count = sample_count
                else:
                    file_handle.write(f"{now},{voltage:.8e}\n")
                    if sample_count % 40 == 0:
                        file_handle.flush() 

    except KeyboardInterrupt:
        print("\nStopping")
    finally:
        dmm.clear()
        dmm.write("DISP MSG,\"                 \"")
        print('kthxbye')

if __name__ == "__main__":
    main()