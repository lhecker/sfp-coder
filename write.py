import sys
import time

import smbus

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <file to flash>")
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    data = f.read()
if len(data) != 0x80:
    print("Invalid rom file. Expected 0x80 bytes.")
    sys.exit(1)

# Checksum byte at offset 0x3f, aka CC_BASE
cc_base = sum(b for b in data[0x00:0x3f]) & 0xff
if data[0x3f] != cc_base:
    print(f"Invalid rom file: CC_BASE checksum error. Expected 0x{cc_base:02x}, got 0x{data[0x3f]:02x}.")
    sys.exit(1)

# Checksum byte at offset 0x5f, aka CC_EXT
cc_ext = sum(b for b in data[0x40:0x5f]) & 0xff
if data[0x5f] != cc_ext:
    print(f"Invalid rom file: CC_EXT checksum error. Expected 0x{cc_ext:02x}, got 0x{data[0x3f]:02x}.")
    sys.exit(1)

bus = smbus.SMBus(1)
rom = bytes(bus.read_byte_data(0x50, i) for i in range(0, 0x80))

if rom == data:
    print("No changes to write.")
    sys.exit(0)

print("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")
for i in range(0x00, 0x80, 0x10):
    print(f"{i:02x}: ", end="")
    for j in range(0x00, 0x10):
        vt_prefix = "\033[91m" if rom[i + j] != data[i + j] else ""
        vt_suffix = "\033[m" if rom[i + j] != data[i + j] else ""
        end = " " if j != 0xf else "\n"
        print(f"{vt_prefix}{data[i + j]:02x}{vt_suffix}", end=end)

print()
print("Found changes. Write? [yN] ", end="")
try:
    if input().lower() != "y":
        sys.exit(0)
except KeyboardInterrupt:
    sys.exit(0)

print("MSA EEPROM password (format: 1a 2b 3c 4d; default: none)? ", end="")
try:
    password = input()
    if password == "":
        password = None
    else:
        password = [int(x, 16) for x in password.split()]
        if len(password) != 4:
            raise ValueError
except KeyboardInterrupt:
    sys.exit(0)
except ValueError:
    print("Invalid password format.")
    sys.exit(1)

if password is not None:
    for i in range(0, 4):
        bus.write_byte_data(0x51, 0x7b + i, password[i])
    time.sleep(0.1)

print()
for i in range(0x00, 0x80):
    if rom[i] != data[i]:
        print(f"Writing 0x{i:02x}: 0x{rom[i]:02x} -> 0x{data[i]:02x}")
        bus.write_byte_data(0x50, i, data[i])
