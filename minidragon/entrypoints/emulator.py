import argparse
import os
import serial  # type: ignore
import sys
import termios
import time
import tty
from io import FileIO
from typing import Any, Final, List, Optional

from ..core import CPUCore, MemoryFilter


ROM_LOCATION: Final[int] = 0x0000
ROM_SIZE: Final[int] = 0x7800
PERIPHERALS_LOCATION: Final[int] = 0x7800
PERIPHERALS_SIZE: Final[int] = 0x800
CART_LOCATION: Final[int] = 0x8000
CART_SIZE: Final[int] = 0x4000
RAM_LOCATION: Final[int] = 0xC000
RAM_SIZE: Final[int] = 0x4000


class ExpansionBus:
    def __init__(self) -> None:
        self.value = 0


class Cartridge:
    def __init__(self, expansion: ExpansionBus, data: bytes, banks: int = 1) -> None:
        self.expansion = expansion
        self.data = data

        # Cartridge bank control.
        self.cb = 0

        # Cartridge input, always 0 for now.
        self.ci = 0

        # Cartridge bank configuration, always 1 executable page for now.
        self.cbc = banks

    def read(self, address: int) -> int:
        if address < 0:
            address = 0
        address = address & 0x3FFF
        address |= (self.cb << 15)

        if address >= len(self.data):
            return 0
        return self.data[address]

    def write(self, address: int, data: int) -> Optional[int]:
        # Right now, cartridges are emulated as read-only.
        return None

    def tick(self, cycles: int, instructions: int) -> None:
        # Nothing happens for carts right now, they're essentially ROM boards.
        pass


class EmptyCartridge(Cartridge):
    def __init__(self, expansion: ExpansionBus) -> None:
        super().__init__(expansion, b"", banks=0)


class Peripheral:
    def __init__(self, slot: int, expansion: ExpansionBus, verbose: bool) -> None:
        # What peripheral slot this is addressed under.
        self.slot = slot
        self.expansion = expansion
        self.verbose = verbose

    def log(self, data: str) -> None:
        if self.verbose:
            print(data, file=sys.stderr)

    def read(self, address: int) -> int:
        return 0

    def write(self, address: int, value: int) -> None:
        pass

    def tick(self, cycles: int, instructions: int) -> None:
        pass


class R6551AP(Peripheral):
    def __init__(self, expansion: ExpansionBus, port: Optional[str], verbose: bool) -> None:
        super().__init__(0, expansion, verbose)

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
        self.__rxw: Optional[float] = None

        self.__stdin: Optional[FileIO] = None
        self.__stdout: Optional[FileIO] = None
        self.__old: Optional[Any] = None
        if self.__port is None:
            os.set_blocking(0, False)
            self.__stdin = os.fdopen(0, 'rb', buffering=0)
            self.__stdout = os.fdopen(1, 'wb', buffering=0)

            # Ensure that the terminal emulator we're under doesn't buffer input before sending to us.
            self.__old = termios.tcgetattr(self.__stdin.fileno())
            tty.setcbreak(self.__stdin.fileno(), termios.TCSANOW)

    def __del__(self) -> None:
        if self.__old and self.__stdin:
            termios.tcsetattr(self.__stdin.fileno(), termios.TCSADRAIN, self.__old)

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

            if self.__stdout is None:
                raise Exception("Logic error, shouldn't have null stdout in non-serial port mode!")
            self.__stdout.write(bytes([byte]))
            self.__stdout.flush()
        else:
            # Might need to open serial port, might be able to use existing.
            conn = self._conn()
            if conn:
                self.tdre = False
                if self.irq:
                    self.irq = self.dsr or self.dcd or self.rdrf or self.tdre
                self.__txw = time.time() + self._time()
                conn.write(bytes([byte]))
            else:
                self.log("Impossible condition, ignoring Tx.")

    def _rxb(self) -> Optional[int]:
        if self.rcs == 0:
            # Misconfigured to read with external receiver clock, which we aren't
            # going to use in hardware. So, refuse to ever read to emulate being
            # configured wrong.
            return None

        if self.__port is None:
            if self.__stdin is None:
                raise Exception("Logic error, shouldn't have null stdin in non-serial port mode!")

            byte = self.__stdin.read(1)
            if byte is None:
                return None

            # Experimentally, an actual VT-102 tends to send characters at about 625
            # bits per second, not the full 9600 bits per second. So, hardcode that
            # here.
            waittime = self._time()
            if waittime < 0.016:
                waittime = 0.016

            self.__rxw = time.time() + waittime
            data = byte[0]

            # Convert delete to backspace (^H) since this is what a VT-100 would send.
            if data == 127:
                data = 8

            return data
        else:
            # Might need to open serial port, might be able to use existing.
            conn = self._conn()
            if conn:
                data = conn.read(1)
                if data:
                    if len(data) > 1:
                        raise Exception("Logic error, got too many bytes back from serial!")

                    # No need to simulate Rx delays with real hardware, so not
                    # setting the Rx wait flag.
                    return int(data[0])
            else:
                self.log("Impossible condition, ignoring Rx.")

            return None

    def tick(self, cycles: int, instructions: int) -> None:
        # Attempt to read a byte from our interface.
        if self.__rxw is not None:
            if self.__rxw <= time.time():
                # Time elapsed for receive.
                self.__rxw = None

        if self.__rxw is None:
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


class CCR(Peripheral):
    def __init__(self, expansion: ExpansionBus, cartridge: Cartridge, verbose: bool) -> None:
        # What peripheral slot this is addressed under.
        super().__init__(7, expansion, verbose)

        self.cartridge = cartridge
        self.cycles = 0
        self.instructions = 0

    def read(self, address: int) -> int:
        if address == 0:
            # Bottom 4 bits are the cartridge bank control, upper 4 are always zeros.
            return self.cartridge.cb & 0xF
        if address == 1:
            # Bottom 4 bits are the cartridge bank configuration, upper 4 are cartridge input.
            return (self.cartridge.cbc & 0xF) | ((self.cartridge.ci & 0xF) << 4)
        if address == 2:
            # 8 expansion bits readable as a register.
            return self.expansion.value & 0xFF

        # No other registers.
        return 0

    def write(self, address: int, value: int) -> None:
        if address == 0:
            # Bottom 4 bits are the cartridge bank control, writing changes the bank.
            self.cartridge.cb = value & 0xF

        if address == 255:
            # Special debug trigger instruction, output CPU cycles and instructions.
            print(f"Current cycles: {self.cycles}, current instructions: {self.instructions}", file=sys.stderr)

    def tick(self, cycles: int, instructions: int) -> None:
        self.cycles = cycles
        self.instructions = instructions


class MiniDragonMemoryFilter(MemoryFilter):
    def __init__(self, peripherals: List[Peripheral], cartridge: Cartridge, verbose: bool) -> None:
        self.peripherals = {p.slot: p for p in peripherals}
        self.cartridge = cartridge
        self.verbose = verbose

    def log(self, data: str) -> None:
        if self.verbose:
            print(data, file=sys.stderr)

    def tick(self, cycles: int, instructions: int) -> None:
        for peripheral in self.peripherals.values():
            peripheral.tick(cycles, instructions)
        self.cartridge.tick(cycles, instructions)

    def read(self, address: int) -> Optional[int]:
        # Bottom part of memory is the ROM file. top 2KB of ROM space is
        # where the peripherals are mapped.
        if address < PERIPHERALS_LOCATION or address >= RAM_LOCATION:
            return None

        if address >= CART_LOCATION:
            return self.cartridge.read(address - CART_LOCATION)

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
            self.log(f"Ignoring write of {hex(data)} to ROM address {address}!")
            return None
        if address >= RAM_LOCATION:
            # RAM is directly writeable, pass the data value on.
            return data
        if address >= CART_LOCATION:
            # Cart space is writeable, pass the data value on.
            return self.cartridge.write(address - CART_LOCATION, data)

        # Calculate peripheral offset, pass off to the peripheral's impl.
        slot = (address - PERIPHERALS_LOCATION) // 0x100
        offset = (address - PERIPHERALS_LOCATION) % 0x100

        if slot in self.peripherals:
            self.peripherals[slot].write(offset, data)

        # System memory is "read only" in this location, nothing gets updated
        # outside of the peripherals themselves.
        return None


def main(boot_rom: str, cartridge: Optional[str], serial_port: Optional[str], verbose: bool) -> int:
    # First, fill the ROM portion with the bootROM file itself.
    with open(boot_rom, "rb") as bfp:
        data = bfp.read()
    if len(data) > ROM_SIZE:
        data = data[:ROM_SIZE]
    if len(data) < ROM_SIZE:
        data = data + b"\x00" * (ROM_SIZE - len(data))

    memory = [0] * 0x10000
    for i, byte in enumerate(data):
        memory[i] = byte

    # Expansion bus is emulated but currently unused. It's only available on the
    # peripheral board but it's wired to all peripherals an the cart slot.
    expansion = ExpansionBus()

    # Load any cartridge presented.
    if cartridge:
        with open(cartridge, "rb") as bfp:
            cdata = bfp.read()
            chw = Cartridge(expansion, cdata)
    else:
        chw = EmptyCartridge(expansion)

    # Hook up peripherals to the system.
    ram_filter = MiniDragonMemoryFilter(
        [
            R6551AP(expansion, serial_port, verbose),
            CCR(expansion, chw, verbose),
        ],
        chw,
        verbose,
    )

    # Calculate how much time a single tick should take as a fraction of a second.
    ticktime = 1.0 / 18000.0

    # Now, instantiate the CPU core and run until a halt instruction is encountered.
    cpu = CPUCore(memory, ram_filter)
    after = time.time()
    while True:
        if cpu.mnemonic == "HALT":
            break

        # Get the timing from the last instruction so we can be accurate about speed.
        cycles = cpu.cycles
        before = after

        cpu.tick()
        ram_filter.tick(cpu.cycles, cpu.ticks)

        # The real CPU runs at ~18.0KHz, simulate that here.
        cycles = cpu.cycles - cycles
        expected = float(cycles) * ticktime
        after = time.time()
        catchup = expected - (after - before)

        if catchup > 0.0:
            waittime = after + catchup
            while (actual := time.time()) < waittime:
                pass

            # Compensate for overrun by rewinding time.
            after = waittime - (actual - waittime)

    return 0


def run() -> None:
    parser = argparse.ArgumentParser(description="A full system emulator for MiniDragon.")
    parser.add_argument(
        "file",
        metavar="FILE",
        help="The bootROM file to emulate.",
    )
    parser.add_argument(
        "-c",
        "--cartridge",
        metavar="ROM",
        type=str,
        default=None,
        help="Attach this cartridge image to the cartridge port.",
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
    sys.exit(main(args.file, args.cartridge, args.serial_port, args.verbose))


if __name__ == "__main__":
    run()
