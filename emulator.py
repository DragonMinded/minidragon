#! /usr/bin/python3
import argparse
import select
import serial  # type: ignore
import sys
import time
from typing import Final, List, Optional
from core import CPUCore, MemoryFilter


ROM_LOCATION: Final[int] = 0x0000
ROM_SIZE: Final[int] = 0x7800
PERIPHERALS_LOCATION: Final[int] = 0x7800
PERIPHERALS_SIZE: Final[int] = 0x800
RAM_LOCATION: Final[int] = 0x8000
RAM_SIZE: Final[int] = 0x8000


class Peripheral:
    def __init__(self, slot: int, verbose: bool) -> None:
        # What peripheral slot this is addressed under.
        self.slot = slot
        self.verbose = verbose

    def log(self, data: str) -> None:
        if self.verbose:
            print(data, file=sys.stderr)

    def read(self, address: int) -> int:
        return 0

    def write(self, address: int, value: int) -> None:
        pass


class R6551AP(Peripheral):
    def __init__(self, port: Optional[str], verbose: bool) -> None:
        super().__init__(0, verbose)

        # Status register bits.
        self.irq = False
        self.dsr = False
        self.dcd = False
        self.tdre = True
        self.rdrf = False
        self.ovrn = False
        self.fe = False
        self.pe = False

        # Control register.
        self.sbn = 1
        self.wl = 8
        self.rcs = 0
        self.sbr = 0

        # Command register.
        self.pmc = 0
        self.pme = 0
        self.rem = 0
        self.tic = 0
        self.ird = 0
        self.dtr = 0

        self.__port = port
        self.__conn: Optional[serial.Serial] = None
        self.__recvd: Optional[int] = None
        self.__txw: Optional[float] = None

    def _baud(self) -> Optional[int]:
        if self.sbr == 1:
            return 50
        elif self.sbr == 2:
            return 75
        elif self.sbr == 3 or self.sbr == 4:
            # Fractional baud rates, unsupported.
            return None
        elif self.sbr == 5:
            return 150
        elif self.sbr == 6:
            return 300
        elif self.sbr == 7:
            return 600
        elif self.sbr == 8:
            return 1200
        elif self.sbr == 9:
            return 1800
        elif self.sbr == 10:
            return 2400
        elif self.sbr == 11:
            return 3600
        elif self.sbr == 12:
            return 4800
        elif self.sbr == 13:
            return 7200
        elif self.sbr == 14:
            return 9600
        elif self.sbr == 15:
            return 19200
        else:
            raise Exception("Logic error, invalid SBR value!")

    def _time(self) -> float:
        baud = self._baud()
        if baud is None:
            raise Exception("No valid baud rate, can't calculate wait!")

        bitwidth = 1.0 / baud

        if self.pme:
            if self.pmc == 0:
                parity = 1
            elif self.pmc == 1:
                parity = 1
            else:
                # Invalid, but calculate anyway.
                parity = 0
        else:
            parity = 0

        bits = self.wl + self.sbn + parity
        return float(bits) * bitwidth

    def _conn(self) -> Optional[serial.Serial]:
        if self.__conn is not None:
            return self.__conn

        # Figure out parameters for serial.
        if self.sbr == 0 or self.rcs == 0:
            # Invalid configuration, we don't support external clock.
            self.log("R6551AP configured for external clock, ignoring Rx/Tx.")
            return None

        baud = self._baud()
        if baud is None:
            # Invalid fractional baud rate, don't support it.
            self.log("R6551AP configured for unsupported baud rate, ignoring Rx/Tx.")
            return None

        if self.wl == 5:
            bytesize = serial.FIVEBITS
        elif self.wl == 6:
            bytesize = serial.SIXBITS
        elif self.wl == 7:
            bytesize = serial.SEVENBITS
        elif self.wl == 8:
            bytesize = serial.EIGHTBITS

        if self.pme:
            if self.pmc == 0:
                parity = serial.PARITY_ODD
            elif self.pmc == 1:
                parity = serial.PARITY_EVEN
            else:
                # Invalid configuration, don't support parity mark/space.
                self.log("R6551AP configured for unsupported mark/space parity, ignoring Rx/Tx.")
                return None
        else:
            parity = serial.PARITY_NONE

        if self.sbn == 0:
            stopbits = serial.STOPBITS_ONE
        else:
            if bytesize == serial.EIGHTBITS and parity != serial.PARITY_NONE:
                stopbits = serial.STOPBITS_ONE
            elif bytesize == serial.FIVEBITS and parity == serial.PARITY_NONE:
                stopbits = serial.STOPBITS_ONE_POINT_FIVE
            else:
                stopbits = serial.STOPBITS_TWO

        self.__conn = serial.Serial(
            port=self.__port,
            baudrate=baud,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=0,
        )
        return self.__conn

    def _txb(self, byte: int) -> None:
        if self.tic == 0:
            # Transmitter disabled.
            self.log("R6551AP transmitter disabled, ignoring Tx.")
            return

        if self.__txw is not None:
            if self.__txw > time.time():
                # Sent another byte when the previous was sending. Drop it.
                self.log("R6551AP dropping Tx byte requested before Tx ready.")
                return

        if self.__port is None:
            # Just output on stdout.
            self.tdre = False
            if self.irq:
                self.irq = self.dsr or self.dcd or self.rdrf or self.tdre
            self.__txw = time.time() + self._time()
            sys.stdout.buffer.write(bytes([byte]))
            sys.stdout.flush()
        else:
            # Might need to open serial port, might be able to use existing.
            conn = self._conn()
            if conn:
                self.tdre = False
                if self.irq:
                    self.irq = self.dsr or self.dcd or self.rdrf or self.tdre
                self.__txw = time.time() + self._time()
                conn.write(bytes([byte]))

    def _rxb(self) -> Optional[int]:
        if self.rcs == 0:
            # Misconfigured to read with external receiver clock, which we aren't
            # going to use in hardware. So, refuse to ever read to emulate being
            # configured wrong.
            return None

        if self.__port is None:
            # Input from stdin.
            rfds, _, _ = select.select([sys.stdin], [], [], 0)
            if not rfds:
                return None
            return sys.stdin.buffer.read(1)[0]
        else:
            # Might need to open serial port, might be able to use existing.
            return None

    def _tick(self) -> None:
        # Attempt to read a byte from our interface.
        read = self._rxb()
        if read:
            # See if we overran the buffer or not.
            if self.__recvd is not None:
                self.log("R6551AP overran Rx buffer, dropping incoming byte.")
                self.ovrn = True
            else:
                self.__recvd = read
                self.rdrf = True
                self.irq = True

        # Attempt to clear the transmit blocked status.
        if self.__txw is not None:
            if self.__txw <= time.time():
                # Time elapsed for transmit.
                self.tdre = True
                self.irq = True
                self.__txw = None

    def read(self, address: int) -> int:
        self._tick()

        register = address & 0x3

        if register == 0:
            # Read receiver data register.
            if self.__recvd is not None:
                val = self.__recvd
                self.__recvd = None
                self.rdrf = False
            else:
                self.log("R6551AP read empty Rx buffer, returning zero.")
                val = 0

            # Ensure that we set/clear the IRQ bit based on if there's
            # another interrupt available.
            if self.irq:
                self.irq = self.dsr or self.dcd or self.rdrf or self.tdre

            return val

        elif register == 1:
            # Read status register.
            val = (
                (0x80 if self.irq else 0x00) +
                (0x40 if self.dsr else 0x00) +
                (0x20 if self.dcd else 0x00) +
                (0x10 if self.tdre else 0x00) +
                (0x08 if self.rdrf else 0x00) +
                (0x04 if self.ovrn else 0x00) +
                (0x02 if self.fe else 0x00) +
                (0x01 if self.pe else 0x00)
            )

            # Clear interrupt bit.
            self.irq = False

            return val

        elif register == 2:
            # Read command register.
            val = (
                ((self.pmc & 0x3) << 6) +
                (0x20 if self.pme else 0x00) +
                (0x10 if self.rem else 0x00) +
                ((self.tic & 0x3) << 2) +
                (0x02 if self.ird else 0x00) +
                (0x01 if self.dtr else 0x00)
            )

            return 0

        elif register == 3:
            # Read control register.
            if self.wl == 8:
                wlv = 0
            elif self.wl == 7:
                wlv = 1
            elif self.wl == 6:
                wlv = 2
            elif self.wl == 5:
                wlv = 3
            else:
                raise Exception("Logic error, invalid WL value!")

            val = (
                (0x80 if self.sbn == 2 else 0x00) +
                (wlv << 5) +
                (0x10 if self.rcs else 0x00) +
                (self.sbr & 0x0F)
            )

            return val

        else:
            raise Exception("Logic error, invalid register!")

    def write(self, address: int, value: int) -> None:
        self._tick()

        register = address & 0x3

        if register == 0:
            # Write transmit data register.
            self._txb(value)

        elif register == 1:
            # Programmed reset.
            self.ovrn = False

            self.rem = 0
            self.tic = 0
            self.ird = 0
            self.dtr = 0

            self.log("R6551AP software reset, clearing overrun flag.")

        elif register == 2:
            # Write command register.
            old_pmc = self.pmc
            old_pme = self.pme

            self.pmc = (value >> 6) & 0x3
            self.pme = (value >> 5) & 0x1
            self.rem = (value >> 4) & 0x1
            self.tic = (value >> 2) & 0x3
            self.ird = (value >> 1) & 0x1
            self.dtr = (value >> 1) & 0x1

            if self.pmc != old_pmc or self.pme != old_pme:
                # Changed parity settings, might need to refresh serial connection.
                self.__conn = None

        elif register == 3:
            # Write control register.
            old_sbn = self.sbn
            old_wl = self.wl
            old_sbr = self.sbr

            # Stop bit number.
            self.sbn = 2 if bool((value >> 7) & 0x1) else 1

            # Word length.
            wl = (value >> 5) & 0x3
            if wl == 0:
                self.wl = 8
            elif wl == 1:
                self.wl = 7
            elif wl == 2:
                self.wl = 6
            elif wl == 3:
                self.wl = 5

            # Receiver clock source.
            self.rcs = (value >> 4) & 0x1

            # Selected Baud Rate.
            self.sbr = value & 0xF

            if self.sbn != old_sbn or self.wl != old_wl or self.sbr != old_sbr:
                # Changed baud, stop or bits settings, might need to refresh serial connection.
                self.__conn = None

        else:
            raise Exception("Logic error, invalid register!")


class MiniDragonMemoryFilter(MemoryFilter):
    def __init__(self, peripherals: List[Peripheral]) -> None:
        self.peripherals = {p.slot: p for p in peripherals}

    def read(self, address: int) -> Optional[int]:
        # Bottom part of memory is the ROM file. top 2KB of ROM space is
        # where the peripherals are mapped.
        if address < PERIPHERALS_LOCATION or address >= RAM_LOCATION:
            return None

        # Calculate peripheral offset, pass off to the peripheral's impl.
        slot = (address - PERIPHERALS_LOCATION) // 0x100
        offset = (address - PERIPHERALS_LOCATION) % 0x100

        if slot in self.peripherals:
            return self.peripherals[slot].read(offset)
        else:
            return 0

    def write(self, address: int, data: int) -> Optional[int]:
        if address < PERIPHERALS_LOCATION:
            # ROM is not writeable, refuse to update the contents.
            return None
        if address >= RAM_LOCATION:
            # RAM is directly writeable, pass the data value on.
            return data

        # Calculate peripheral offset, pass off to the peripheral's impl.
        slot = (address - PERIPHERALS_LOCATION) // 0x100
        offset = (address - PERIPHERALS_LOCATION) % 0x100

        if slot in self.peripherals:
            self.peripherals[slot].write(offset, data)

        # System memory is "read only" in this location, nothing gets updated
        # outside of the peripherals themselves.
        return None


def main(boot_rom: str, serial_port: Optional[str], verbose: bool) -> int:
    # First, fill the ROM portion with the bootROM file itself.
    with open(args.file, "rb") as bfp:
        data = bfp.read()
    if len(data) > ROM_SIZE:
        data = data[:ROM_SIZE]
    if len(data) < ROM_SIZE:
        data = data + b"\x00" * (ROM_SIZE - len(data))

    memory = [0] * 0x10000
    for i, byte in enumerate(data):
        memory[i] = byte

    # Hook up peripherals to the system.
    ram_filter = MiniDragonMemoryFilter([
        R6551AP(serial_port, verbose),
    ])

    # Now, instantiate the CPU core and run until a halt instruction is encountered.
    cpu = CPUCore(memory, ram_filter)
    while True:
        if cpu.mnemonic == "HALT":
            break
        cpu.tick()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A full system emulator for MiniDragon.")
    parser.add_argument(
        "file",
        metavar="FILE",
        help="The bootROM file to emulate.",
    )
    parser.add_argument(
        "-s",
        "--serial-port",
        metavar="PORT",
        type=str,
        default=None,
        help="Emulate serial over this serial port instead of stdin/stdout.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output of emulator state to stderr.",
    )

    args = parser.parse_args()
    sys.exit(main(args.file, args.serial_port, args.verbose))
