# MiniDragon Assembler and Compiler Utils

A collection of utilities for working with MiniDragon assembly and MiniPy source files.

## Installation

To install these files, use the following one-liner:

```
pipx install git+https://github.com/DragonMinded/minidragon.git
```

To upgrade once you've installed, use the following one-liner:

```
pipx upgrade minidragon
```

To uninstall these files, use the following one-liner:

```
pipx uninstall minidragon
```

For help and instruction on setting up `pipx` on your computer, visit [pipx's installation page](https://pipx.pypa.io/stable/installation/).

## Utilities

The following utilities will be installed into your system path by `pipx`:

 - `minidragon-assembler` - Utility to take valid MiniDragon .S assembly files and output assembled binary suitable for burning to an EPROM or running in the emulator.
 - `minidragon-compiler` - Utility to take valid MiniPy .py source files and output assembly files suitable for linking into a ROM using the assembler.
 - `minidragon-emulator` - Utility to take an assembled .bin file and emulate the MiniDragon executing this ROM.
 - `minidragon-simulator` - Utility to take either a full .S listing or a .bin assembled ROM file and simulate the CPU on a line-by-line-basis.
