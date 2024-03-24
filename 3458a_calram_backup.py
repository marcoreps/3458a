import pyvisa
import sys

def mread(instr, lo, hi):
	instr.write("TRIG HOLD")
	instr.write("QFORMAT NUM")
	# Addresses must be even
	assert lo & 1 == 0
	assert hi & 1 == 0
	l = list()
	for i in range(lo, hi, 2):
		j = int(instr.query("MREAD %d" % i))
		if j < 0:
			j = 65536 + j
		l.append(j)
	return l

def nvram(instr,  fname="hp3458.calram.bin"):
	l=mread(instr, 0x60000, 0x60000 + 2048 * 2)
	fo = open(fname, "w")
	for i in l:
		fo.write("%c" % (i >> 8))
	fo.close()

rm = pyvisa.ResourceManager()
instr =  rm.open_resource("GPIB0::22::INSTR")
instr.timeout = 200000
instr.clear()
instr.write("RESET")
instr.write("END ALWAYS")
instr.write("OFORMAT ASCII")
instr.write("BEEP")
print(instr.query("ID?"))

nvram(instr)
