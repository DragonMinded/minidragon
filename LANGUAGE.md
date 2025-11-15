# MiniPy Language Specification

Included in the software tooling for the MiniDragon CPU is a compiler that takes a variant of Python informally referred to as MiniPy and emits assembly listings that can be assembled by the assembler to burn onto an EPROM, run through the included system emulator or run through the simulator/debugger. This document serves as the langauge specification for MiniPy.

## Lexical Analysis

MiniPy entirely reuses the Python grammar for source file parsing. For the full grammar specification you can see the [Full Grammar Specification](https://docs.python.org/3/reference/grammar.html) from the Python documentation. The lexer and parse tree uses [LibCST](https://github.com/Instagram/LibCST). What this means in practice is that any file which is valid syntax according to Python will also be valid syntax according to MiniPy.

## Type System

Unlike standard Python, MiniPy requires full type specification to compile. There are no objects so there is no duct typing. Instead, type inference in the compiler verifies the soundness of expressions and function calls based on the declared types. The standard data types include integers, strings, characters and booleans. Additionally, you have the option of declaring any variable constant, at which point the compiler will forbid any mutation of the variable such as assignment or string modification after the variable has been declared and assigned to.

Types are provided in the same manner as type hints in standard Python. This means that function parameters and returns are required to be typed. Additionally, all variable definitions are required to be typed. Note that MiniPy treats the first assignment of a local variable that hasn't been declared global as the definition of the variable. Unlike some old flavors of C and like Python, variable definitions are allowed anywhere. Unlike Python and like C langauges, however, variable scope is limited to the block of code in which the variable was defined. Like standard Python, it's possible to declare a variable with a type and not assign to it until later. Note that if you attempt to use a variable after declaring it but before initializing it, the compiler will flag an error on the line.

MiniPy will perform all expression evaluation at the width of the destination in an assignment, function call or return statement. Said in another way, if you assign the result of an expression to an 8 bit integer, the intermediate calculations will all be done with 8 bit data types as well. Integers that are larger than the data type will be truncated at the point of reference in the expression. Integers that are smaller than the data type will be zero-extended or sign-extended, depending on whether they are unsigned or signed integers, at the point of reference in the expression. This goes for expressions in a function call parameter as well as expressions in a return statement. In the former, the width of the parameter itself according to the function definition will be used. In the latter, the function return type width will be used.

The valid types available to MiniPy programs are as follows.

`uint8`

 > An 8 bit unsigned integer, capable of representing values from 0 through 255. Takes up one byte of memory on the stack.

`int8`

 > An 8 bit two's compliment signed integer, capable of representing values from -128 through 127. Takes up one byte of memory on the stack.

`uint16`

 > A 16 bit unsigned integer, capable of representing values from 0 through 65535. Takes up two bytes of memory on the stack, stored as big-endian.

`int16`

 > A 16 bit two's compliment signed integer, capable of representing values from -32768 through 32767. Takes up two bytes of memory on the stack, stored as big-endian.

`uint32`

 > A 32 bit unsigned integer, capable of representing values from 0 through 4294967295. Takes up four bytes of memory on the stack, stored as big-endian.

`int32`

 > A 32 bit two's compliment integer, capable of representing values from -2147483648 through 2147483647. Takes up four bytes of memory on the stack, stored as big-endian.

`char`

 > An 8 bit ASCII character, capable of holding any of the 8 bit ASCII values including the null byte. Takes up one byte of memory on the stack or one byte of memory in a string.

`str`

 > A null-terminated ASCII string, capable of holding up to 127 characters including the null terminator byte. Implemented as a 16 bit pointer to a memory address in RAM. Takes up two bytes of memory on the stack, stored as a big-endian pointer. Note that non-constant strings are required to specify the desired maximum storage length. This is done using bracket notation as demonstrated in examples below. The exception to this is in functions returning strings which explicitly return a variable or constant. In this case, you are free to declare that your function returns a `str` without using bracket notation to define a maximum storage length.

`bool`

 > A boolean, holding the value of `True` or `False`. Under the hood this is mapped to a signe byte holding either the value `0x00` for `False` or `0xFF` for `True`.

`void`

 > The lack of a value. This is only ever used to specify functions that do not return a value and cannot be used for function parameters, local or global variables.

Additionally, any parameter, function return or local variable can be declared constant by using the `const[]` modifier. When a variable is made constant it cannot be assigned to or modified after its declaration. Attempting to do so will generate a compile error on the offending line. Declaring a global varible as `const` will cause the compiler to place it into the code section of the compiled output.

Examples of various types are as follows.

`a: int16`

 > Declare a local variable `a` as a signed 16 bit integer. The compiler will allocate space on the stack for this variable at time of allocation.

`a: const[uint32] = b + 37`

 > Declare a local variable `a` as a constant unsigned 32 bit integer and assign it the value of `b + 37`. Note that it is a compile error to declare a constant variable without assigning it a value since it would be impossible to mutate the value at a later time.

`a: str[32] = ""`

 > Declare a local variable `a` as a string with a maximum storage of 32 bytes including the null terminator and initialize it to the empty string.

`def func(param1: int8, param2: const[int8]) -> bool: ...`

 > Declare a function which takes two parameters and returns a boolean. `param1` is an 8 bit signed integer and `param2` is a constant 8 bit signed integer. This means that within the function code is free to assign to `param1` but attempting to modify `param2` will result in a compiler error. The compiler will use the types of the parameters and return to allocate space on the stack for the parameters and the return itself. Note that the example provides an ellipses (`...`) instead of a function body. This would normally result in a compiler error unless you were declaring an `extern` function but has been shown here to demonstrate how a function prototype might look without needing to specify a function body.

`def func(param: const[str]) -> void: ...`

 > Declare a function which takes a single string parameter and does not return a value. `param` is a constant string, meaning the function cannot modify or mutate the string in any way.

## Supported Python Features

MiniPy only supports a limited subset of Python's language features. Care has been taken to conform to Python behavior and expectations within that subset wherever possible. However, you are coding for an extremely limited and slow custom ISA so some deviations and compromises should be expected.

Please note that while standard Python is fully object-oriented, objects do not exist in MiniPy. There is no dotted notation support for accessing object attributes, no ability to define classes, and no support for built-in objects. There are no higher level data types such as tuples, dictionaries, sets, lists, or similar. Data types that are supported have concrete limits to their use.

### Integer Support

MiniPy supports integer arithmetic on 8 bit, 16 bit and 32 bit integers. It has support for both signed and unsigned arithmetic, although divide and modulo are only implemented for unsigned integers. Unlike standard Python, you must specify the width of your integer variables and there is no support for integers that do not fit within a 32 bit data type. The following operations are supported for unsigned integers: `+` (addition), `-` (subtraction), `*` (multiplication), `/` (division), `%` (modulo), `&` (bitwise and), `|` (bitwise or), `~` (bitwise not), `^` (bitwise xor), `<<` (logical shift left), `>>` (logical shift right). Additionally, all previously listed operations except for `/` and `%` are supported for signed integers. Additionally, Python's augmented assignment operators are fully supported for all operations that are supported normally.

Integer arithmetic that causes overflow does not automatically resize the integer to a larger version so care must be taken to choose the integer data type that will adequately fit the calculations you wish to perform. Do note that larger integers are slower to operate on due to the MiniDragon being an 8 bit CPU at its core. Therefore, there is a direct trade-off between range of integers available and the speed at which calculations against those integers can be done. For the best speed, stick with 8 bit integers for everything that does not need more as most basic operations are mapped directly to CPU instructions.

Examples of various operations are as follows.

`a: uint8 = b + c`

 > Adds the integers `b` and `c` together and places the result into a newly-defined variable `a`. The operation will be performed with 8 bits of precision due to the destination of the expression being an 8 bit integer. If `b` or `c` are larger integers they will be truncated to 8 bits before the addition is performed.

`a += 5`

 > Adds 5 to the already-defined integer `a`. Note that this requires `a` to already exist since it is adding 5 to it, so `a` will have been defined with a type on a previous line.

`a: int16 = b - c`

 > Subtracts the value in `c` from `b` and places the result into a newly-defined variable `a`. The operation will be performed with 16 bits of precision. If `b` or `c` are larger than 16 bits, they will be truncated to 16 bits before the operation is performed. If `b` or `c` are smaller than 16 bits, they will be sign-extended to 16 bits before the operation is performed due to the fact that the result of the operation is a signed integer. If `a` was instead defined as a `uint16` then smaller integers would be zero-extended instead.

`a = (a + 1) & 0x3F`

 > Caculates the value of `a + 1` and then boolean ands the result against `0x3F` before assigning the result back to `a`. This effectively creates a counter that will increment `a` by `1` whenever it is called until it hits `63` where it will wrap back around to `0` on the next execution.

### String Support

MiniPy supports a string data type and basic operations on strings. Strings work similarly to their counterpart in Python and unlike `char *` style arrays in C-like languages. That is, strings are passed by value, not by reference. Assigning a string to a variable makes a copy of that string such that modifying the variable later will not affect what it was assigned from. Strings support indexing by both an integer to access the character at a specific index as well as indexing by slice in order to return a substring consisting of the characters at the beginning to the end index.

Unlike Python, MiniPy lets you assign a character to an index in a string. This is because strings are mutable in MiniPy. Note that MiniPy only supports strings up to 127 characters in length, and has no support for non-ASCII values in strings. Unlike Python, each individual character in a string has the data type of `char`, not `str`. That means that performing an operation such as `string[5]` will return a `char` data type, whereas performing an operation such as `string[5:6]` will return a `str` data type.

Note that, for speed reasons, when the compiler can prove that there is no way to accidentally cause aliasing issues, strings will be represented under the hood as a reference to another string instead of a full copy. This only happens with constant strings that are assigned to from a string literal, a global constant string, a function marked as returning a constant string, or another local constant string that was assigned to from one of these categories. Functions are only allowed to be marked as returning a constant string if the value they are returning fits within one of these categories as well. This support for references under the hood extends to string function parameters that are marked as constant.

### Boolean Support

MiniPy supports a boolean data type to represent comparison expressions. It has limited support for automatic conversion from truthy values to boolean values, specifically when non-booleans are used in `if` statements, `while` loops and conditional expressions. In the case of explicit or implicit conversion to boolean, Python's truthy rules apply to MiniPy. Integers are seen as truthy if they are non-zero, and falsey when they are zero. Strings are considered truthy if they contain one or more characters, and falsey if they are empty or zero-length. Characters are considered truthy when they represent anything other than the null byte, and falsey when they represent the null byte. Internally, `False` is represented as a byte with all bits cleared (`0`) and `True` is represented by a byte with all bits set (`255`). This only matters in the case of `peek()` and `poke()` which are documented below.

### Function Support

MiniPy supports defining functions as well as calling functions in a similar fashion to standard Python. Parameters, including strings, are passed to functions by value except in very specific cases regarding string constants. Full support for default arguments is included, so if you specify a default for a given argument you do not need to provide a value when calling the function. Similarly, support for calling functions with keyword arguments is also available. This can come in handy when you want to specifically override only some defaults for a particular function. Note that MiniPy does not support dictionaries or lists, so support for `*args` and `**kwargs` is not available.

Function calls are handled on the stack, meaning that functions are allowed to call themselves recursively. Due to the fact that strings are assigned by value, it is safe to use strings in recursive functions. All other supported data types are similarly supported for recursive functions. Due to the fact that there are no interrupts in the MiniDragon CPU, there is no support for threading or and multi-processing support. Therefore, functions do not need to worry about reentrancy.

## Compiler Intrinsics

Standard Python has support for a plethora of built-in functions. MiniPy replicates support for only a limited subset of these functions. Additionally, it adds a few intrinsics of its own. All supported intrinsics are documented here. The standard Python built-ins which MiniPy supports are listed below. In general, these should behave the same as their standard Python counterparts unless documented otherwise. For standard Python documentation of these intrinsicts, please see the [Built-In Functions](https://docs.python.org/3/library/functions.html)
documentation.

`len(str)`

 > Given a string literal or variable as its only argument, returns the length of the string in characters (not including the null terminator) as a `uint8`. Note that this only works with strings up to 127 characters long as that is the supported length limit of strings in MiniPy

`str(obj)`

 > Given any supported data type, returns a string conversion of that data type. Supports integers, booleans, characters and other strings. For strings and characters, the literal value as a string will be returned. For integers, the conversion of that integer to a decmial number including a negative sign will be returned. For booleans, the string "True" or "False" will be returned depending on the value of the boolean.

`int(obj)`

 > Given a string, integer or boolean, returns an integer conversion of that data type. For Strings, the conversion to an integer including a potential negative sign will be returned. For integers, the number passed in will be returned. For booleans, the number 1 or 0 will be returned for `True` and `False` which is identical to standard Python.

`abs(int)`

 > Given a signed integer, returns the absolute value of that signed integer at the same integer width.

`bool(obj)`

 > Given any supported data type, returns a boolean representing the truthiness of the data type passed in. For strings, returns `True` for any string that is not zero-length, and `False` for empty or zero-length strings. For integers, returns `True` for all nonzero numbers and `False` for zero. For booleans, returns the value passed in. For characters, returns `True` for all characters that are not the null byte, and `False` for the null byte.

`chr(int)`

 > Given an integer, returns the character equivalent of that integer.

`ord(char)`

 > Given a character, returns the integer equivalent of that character.

`hex(int)`

 > Given an integer, returns a string representing the hexidecimal value of the integer, including the `0x` prefix, mirroring standard Python.

`min(int, int)`

 > Given two integers, returns whichever one is smallest in magnitude.

`max(int, int)`

 > Given two integers, returns whichever one is the largest in magnitude.

`range(int, int=None, int=None)`

 > Given one, two or three integers, returns an interator useful in `for` statements. Note that this is only supported in `for` statements since MiniPy has no support for iterables otherwise. For more details on the parameters, please see Python's [range](https://docs.python.org/3/library/functions.html#func-range) documentation.

Additionally, MiniPy specifies a few intrinsics of its own. The MiniPy specific intrinsics are documented below.

`peek(addr, length=None)`

 > Given a 16 bit integer interpreted as a raw memory address, peek at that memory address and return the value contained therein. The return type of peek is dependent on the variable being assigned to in the expression that it is used in. When assigning to an 8 bit integer, peek will read the byte at the memory location and return that as an 8 bit integer. When assigning to a 16 bit integer, peek will read the two bytes at the memory address and subsequent memory address and interpret and return the value as a big-endian 16 bit integer. When assigning to a 32 bit integer, peek will read the four bytes at the memory address and subsequent three memory addresses and interpret and return the value as a big-endian 32 bit integer. When assigning to a character, peek will read the byte at the memory address and return it as a character. When assigning to a boolean, peek will read the byte at the memory address and return `True` for a non-zero byte and `False` for a zero byte. When assigning to a string, peek will perform a string copy starting at the given memory address until it encounters a null terminator byte. Optionally, for strings, you can specify a second parameter as an integer which will be treated as the length to copy. Strings longer than that will be truncated when the length limit is hit, and strings equal to or less than that length will be copied in their entirity.

`poke(addr, obj)`

 > Given a 16 bit integer interpreted as a raw memory address and a value to store, stores that value at that address. For integers, stores the value starting at that address in big-endian. For 8 bit integers, this only modifies the byte at the specified address. For 16 bit integers, this modifies the specified and subsequent byte. For 32 bit integers, this modifies the specified and subsequent three bytes. For characters, stores the character as a byte at the address specified. For booleans, stores either 0 or 255 depending on whether the value is `False` or `True`. For strings, copies the specified string starting at the memory address until the end of the string is reached. Note that the null byte is copied in this instance.

`cast(type, obj)`

 > Given a valid MiniPy type and an object, cast that object to that type. Currently only supports casting `uint16` to `str` and `str` to `uint16`. When performing a cast from a string to an integer, the resulting value that is returned is the memory address that the string resides at. When performing a cast from an integer to a string, the resulting value is a string that points at the given memory address.

`fixed(value, fracbits=8)`

 > Given a floating point value and an optional fractional bits, converts that value to a fixed point integer that represents the decimal approximation of the floating point value. Note that in MiniPy, fixed point integers are always 32 bits wide.

## Import System

MiniPy supports relative imports similar to standard Python. Note that since MiniPy has no objects, you must use the `from <module> import X` syntax for importing. You can perform a star import much like standard Python, or you can explicitly specify the functions, global variables and global constants that you wish to import from the other module. Note that much like standard Python, importing only makes the references to those symbols available locally. Functions and variables that are imported from another module will work identically to functions and variables defined in the current module. The import system works similarly to standard Python where a module saved as `foo.py` is referred to as `foo` within the import statement. Modules can exist in subdirectories relative to the module performing the import, in which case you would specify the module using Python's dotted notation.

The compiler supports providing one or more library directories where it will additionally look for modules to import from if the module is not found in the directory relative to the currently compiled code. This is done through the `-l` or `--lib` flag. The resolution order is to check for local modules matching the specification first, and then to check each library path in the order that the libraries were specified on the command line. For instance, take the following directory layout, compiling `foo.py` by invoking the compiler in the top level directory `/example/` with the command-line `python3 compiler.py --lib lib/ src/foo.py`. When compiling `foo.py` it attempts to import with the line `from bar.baz import bla`. The compiler will check for a `src/bar/baz.py` file first since this is the directory `foo.py` exists in, and failing to find that will look for a `lib/bar/baz.py` file in the library directory specified.

```
/example/
|-- lib/
|   +-- bar/
|       |-- baz.py
|       +-- qux.py
+-- src/
    +-- foo.py
```

To reference a constant, variable or function that is defined only in assembly, you can use the `extern[]` modifier in the type definition for the varible or function. This functions similarly to importing the function or variable from another module in that it makes the thing you're declaring extern available for use within that module. Note that it is perfectly valid to import variables or functions from another MiniPy module that are declared extern. Under the hood, the `extern[]` modifier simply adds the variable type or function prototype to the list of available functions and assumes that there is a global label with a matching name which will be found in the final assembly listing when linking a full ROM.

Examples of using the import system are as follows.

`from hardware.serial import serial_init, serial_clear, serial_send`

 > Looks for the identifiers `serial_init`, `serial_clear` and `serial_send` in the module which implements `hardware.serial` and makes them available in the current module.

`def func(param1: int16, param2: int32) -> extern[bool]: ...`

 > Defines a function prototype for `func` which takes two parameters and returns a boolean. Note the `extern[]` modifier as well as the ellipses (`...`). The compiler will emit code that refers to the global label `func` which should be implemented in an assembly file and linked into the final build. Note also that it is possible to declare functions as extern instead of importing them from other modules but it is heavily recommended to not do this because prototypes could get out of sync with the actual function implementation. If this happens, the compiler will generate incorrect code to call the function and you will most likely end up with a crash. So, it's best to leave `extern[]` functions and variables for when you need to implement something in pure assembly and reference it from within MiniPy code.

## Included Libraries

MiniPy ships with a stdlib that was implemented in assembly as well as several libraries of functions implemented in MiniPy itself. Note that under most circumstances you should not need to call the assembly stdlib directly as the functionality has been mapped onto standard Python operations. However, if you so desire, you can call the functions directly in your code.

## Application Binary Interface

Since the MiniDragon ISA is stack-based with an accumulator, it should come as no surprise that function parameters, local variables, the function return and the return address are placed onto the stack. If you are looking to write functions in assembly which interop with MiniPy code it is important to respect the ABI otherwise you will most likely get a crash. The easiest way to conform to the interface for a given function is to simply let the compiler generate the function stub for you. Define the function with its parameters and return in a module, return a dummy value, compile it, and copy the skeleton out of the assembly listing.

The MiniDragon CPU uses a standard stack that starts at the top of memory and grows down. A push operation will decrement the PC register and then store the value at the memory location pointed at by PC. A pop operation will load the value from the memory location pointed at by PC and then increment the PC register. Function parameters are always provided on the stack even when they could fit in the A, U or V registers. They are pushed onto the stack in the order that they appear in the function definition. When a function is called, after the compiler pushes all of the parameters onto the stack, the actual call operation will push the address of the instruction after the call onto the stack as a big-endian 16 bit address and then jump to the first byte of the function. That means upon entering a function you should expect the PC register to point at the first byte of the return address in memory with the second byte in the next memory address.

When leaving a function, a ret operation is used to pop the return address from the stack and jump to it. This means that when you leave a function you are expected to have the PC register pointing at the first byte of the return address on the stack. When that return address is popped, the PC will be incremented by 2 and should point at the first byte of the return value. The calling code will expect to pop that value from the stack which should return the PC register to the location that it pointed at before any function parameters were pushed onto the stack. That means that it is the called function's responsibility to move the return address and return value when appropriate. This will be necessary when the function parameters take more space on the stack than the return value. Since the calling code expects the parameters to be "consumed" by the called function it will not attempt to pop the parameters off the stack when execution is returned to it after the ret operation.

Note that in cases where the return value takes more space on the stack than the parameters the compiler will insert padding bytes onto the stack so that the called function does not need to relocate the return pointer down the stack to make room for the return value. If the length of all parameters exactly equals or surpasses the size of the return value (or the function is a `void` return) then no padding will be inserted. If you do not want this and you are willing to relocate the return value and return pointer on the stack even when padding bytes could be inserted for you, you can use the `nopad[]` modifier on the function's return type. Using `nopad[]` will instruct the compiler not to insert padding bytes under any circumstance and you will be responsible for moving the return pointer as well as locating the return value on the stack manually.

## Compiler Optimizations

Regardless of whether the optimize code flag has been passed to the compiler, the compiler will attempt to evaluate any constants found in the code it is compiling. That means if you have an expression whose value is known at compile-time, the compiler will not emit code to calculate that expression. Instead, the value of that expression as calculated at compile time will be inserted into the compiled assembly listing instead. The compiler is aware of global and local constants which are known at compile time in its evaluation of whole or partial expressions that can be optimized to a single value.

Additionally, when the compiler has been instructed to do so with the optimize flag (`-z` or `--optimize`) it will make passes over the assembly that it produces until it can no longer find optimizations to perform. This usually results in code that is smaller and runs faster but has the potential to accidentally emit incorrect code. Care has been taken to only perform optimizations that are provably safe and do not alter the semantics of the code at all. However, since compiler optimization passes are effectively pattern matching heuristics, it is possible that the compiler may get things wrong. The compiler will look for things such as redundant loads and stores, redundant stack moving operations, groups of instructions that are performed simply to check the zero or carry flag which can be reduced to equivalent smaller groups, conditional jumps based on constants and redundant stack operations when immediate operations could be substituted.
