import os
import sys

import smbus

bus = smbus.SMBus(1)
rom = bytes(bus.read_byte_data(0x51, i) for i in range(0, 0x80))

if os.isatty(sys.stdout.fileno()):
    print("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")
    for i in range(0x00, 0x80, 0x10):
        print(f"{i:02x}: ", end="")
        for j in range(0x00, 0x10):
            end = " " if j != 0xf else "\n"
            print(f"{rom[i + j]:02x}", end=end)
else:
    sys.stdout.buffer.write(rom)
