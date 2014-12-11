# Configuration file for Rambo-Uploader

import loggers

# Path to avrdude
avrdude_path="avrdude"
# Type of ICSP programmer for Atmega32u2.
m32u2_icsp_programmer="jtag2isp"
# Type of ICSP programmer for Atmega2560
m2560_icsp_programmer="jtag2isp"
# Type of programming through serial
serial_programmer="wiring"
# Port (USB serial number) of ICSP Programmer connected to Atmega32u2
m32u2_icsp_port="usb:402671"
# Port (USB serial number) of ICSP Programmer connected to Atmega2560
m2560_icsp_port="usb:402903"
# Path to Atmega32u2 bootloader
m32u2_bootloader_path="bootloaders/RAMBo-usbserial-DFU-combined-32u2.HEX"
# Path to Atmega2560 bootloader
m2560_bootloader_path="bootloaders/stk500boot_v2_mega2560.hex"
# Serial port for Test Jig Controller. Set to None to use serial number
#controller_port="/dev/ttyACM0"
controller_port=None
# Serial number for Test Jig controller
#controller_snr="640323730343512190C0"
#controller_snr="64036353430351100180"
controller_snr="6403237303435101B0A1"
# Serial port for Device Under Test. Set to None to auto-detect
#target_port="/dev/ttyACM1"
target_port=None
# List of RAMBo board serial numbers to ignore if auto-detecting target. Useful if you have printers connected to the same PC.
#ignore_rambo_snr=("640323738333519081D1", )
ignore_rambo_snr=None

# Program the Atmega32u2 and Atmega2560 through ICSP (required if the fuses are not yet set or bootloader not flashed yet)
icsp_program=False
# Verify flash after ICSP programming
icsp_verify=True
# Delay before testing after we power on the power supply. Some power supply require a bit of time before they provide power.
powering_delay=1

log_level=3

# Path to the test firmware
test_firmware_path="bootloaders/test_firmware.hex"
# Path to the final retail firmware
vendor_firmware_path="bootloaders/vendor_firmware.hex"

# Disable logs
#logger = NoLogs()

# Use PostgreSQL Database
#database_host="localhost"
#database_name="rambotest"
#database_user="rambo"
#database_password="uploader"
#logger = PostgresDatabase(database_host, database_name,
#                          database_user, database_password)

# Text log
#logger = TextLogger("results.txt")

# JSON log
#logger = JsonLogger("results.csv")

# CSV log
#logger = CSVLogger("results.csv")

# Multiple logs
logger = loggers.MultiLogger([loggers.TextLogger("results.txt"),
                      loggers.JsonLogger("results.json"),
                      loggers.CSVLogger("results.csv")])
