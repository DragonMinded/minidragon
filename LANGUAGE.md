# MiniPy Language Specification

Included in the software tooling for the MiniDragon CPU is a compiler that takes a variant of Python informally referred to as MiniPy and emits assembly listings that can be assembled by the assembler to burn onto an EPROM, run through the included system emulator or run through the simulator/debugger. This document serves as the langauge specification for MiniPy.

## Lexical Analysis

MiniPy entirely reuses the Python grammar for source file parsing. For the full grammar specification you can see the [Full Grammar Specification](https://docs.python.org/3/reference/grammar.html) from the Python documentation. The lexer and parse tree uses [LibCST](https://github.com/Instagram/LibCST). What this means in practice is that any file which is valid syntax according to Python will also be valid syntax according to MiniPy.

## Type System

Unlike standard Python, MiniPy requires full type specification to compile. There are no objects so there is no duct typing. Instead, type inference in the compiler verifies the soundness of expressions and function calls based on the declared types. The standard data types include integers, strings, characters and booleans. Additionally, you have the option of declaring any variable constant, at which point the compiler will forbid any mutation of the variable such as assignment or string modification after the variable has been declared and assigned to.

Types are provided in the same manner as type hints in standard Python. This means that function parameters and returns are required to be typed. Additionally, all variable definitions are required to be typed. Note that MiniPy treats the first assignment of a local variable that hasn't been declared global as the definition of the variable. Unlike some old flavors of C and like Python, variable definitions are allowed anywhere. Unlike Python and like C langauges, however, variable scope is limited to the block of code in which the variable was defined. Like standard Python, it's possible to declare a variable with a type and not assign to it until later. Note that if you attempt to use a variable after declaring it but before initializing it, the compiler will flag an error on the line.

MiniPy will perform all expression evaluation at the width of the destination in an assignment, function call or return statement. Said in another way, if you assign the result of an expression to an 8 bit integer, the intermediate calculations will all be done with 8 bit data types as well. Integers that are larger than the data type will be truncated at the point of reference in the expression. Integers that are smaller than the data type will be zero-extended or sign-extended, depending on whether they are unsigned or signed integers, at the point of reference in the expression. This goes for expressions in a function call parameter as well as expressions in a return statement. In the former, the width of the parameter itself according to the function definition will be used. In the latter, the function return type width will be used.

The valid types available to MiniPy programs are as follows.

---

`uint8`

 > An 8 bit unsigned integer, capable of representing values from 0 through 255. Takes up one byte of memory on the stack.

---

`int8`

 > An 8 bit two's compliment signed integer, capable of representing values from -128 through 127. Takes up one byte of memory on the stack.

---

`uint16`

 > A 16 bit unsigned integer, capable of representing values from 0 through 65535. Takes up two bytes of memory on the stack, stored as big-endian.

---

`int16`

 > A 16 bit two's compliment signed integer, capable of representing values from -32768 through 32767. Takes up two bytes of memory on the stack, stored as big-endian.

---

`uint32`

 > A 32 bit unsigned integer, capable of representing values from 0 through 4294967295. Takes up four bytes of memory on the stack, stored as big-endian.

---

`int32`

 > A 32 bit two's compliment integer, capable of representing values from -2147483648 through 2147483647. Takes up four bytes of memory on the stack, stored as big-endian.

---

`char`

 > An 8 bit extended ASCII character, capable of holding any of the 8 bit extended ASCII values including the null byte. Takes up one byte of memory on the stack or one byte of memory in a string.

---

`str`

 > A null-terminated extended ASCII string, capable of holding up to `127` characters including the null terminator byte. Implemented as a 16 bit pointer to a memory address in RAM. Takes up two bytes of memory on the stack, stored as a big-endian pointer. Note that non-constant strings are required to specify the desired maximum storage length. This is done using bracket notation as demonstrated in examples below. The exception to this is in functions returning strings which explicitly return a variable or constant. In this case, you are free to declare that your function returns a `str` without using bracket notation to define a maximum storage length.

---

`bool`

 > A boolean, holding the value of `True` or `False`. Under the hood this is mapped to a single byte holding either the value `0x00` for `False` or `0xFF` for `True`.

---

`void`

 > The lack of a value. This is only ever used to specify functions that do not return a value and cannot be used for function parameters, local or global variables.

Additionally, any parameter, function return or local variable can be declared constant by using the `const[]` modifier. When a variable is made constant it cannot be assigned to or modified after its declaration. Attempting to do so will generate a compile error on the offending line. Declaring a global varible as `const` will cause the compiler to place it into the code section of the compiled output.

Examples of various types are as follows.

---

`a: int16`

 > Declare a local variable `a` as a signed 16 bit integer. The compiler will allocate space on the stack for this variable at time of allocation.

---

`a: const[uint32] = b + 37`

 > Declare a local variable `a` as a constant unsigned 32 bit integer and assign it the value of `b + 37`. Note that it is a compile error to declare a constant variable without assigning it a value since it would be impossible to mutate the value at a later time.

---

`a: str[32] = ""`

 > Declare a local variable `a` as a string with a maximum storage of 32 bytes including the null terminator and initialize it to the empty string.

---

`def func(param1: int8, param2: const[int8]) -> bool: ...`

 > Declare a function which takes two parameters and returns a boolean. `param1` is an 8 bit signed integer and `param2` is a constant 8 bit signed integer. This means that within the function code is free to assign to `param1` but attempting to modify `param2` will result in a compiler error. The compiler will use the types of the parameters and return to allocate space on the stack for the parameters and the return itself. Note that the example provides an ellipses (`...`) instead of a function body. This would normally result in a compiler error unless you were declaring an `extern` function but has been shown here to demonstrate how a function prototype might look without needing to specify a function body.

---

`def func(param: const[str]) -> void: ...`

 > Declare a function which takes a single string parameter and does not return a value. `param` is a constant string, meaning the function cannot modify or mutate the string in any way.

## Supported Python Features

MiniPy only supports a limited subset of Python's language features. Care has been taken to conform to Python behavior and expectations within that subset wherever possible. However, you are coding for an extremely limited and slow custom ISA so some deviations and compromises should be expected.

Please note that while standard Python is fully object-oriented, objects do not exist in MiniPy. There is no dotted notation support for accessing object attributes, no ability to define classes, and no support for built-in objects. There are no higher level data types such as tuples, dictionaries, sets, lists, or similar. Data types that are supported have concrete limits to their use.

### Integer Support

MiniPy supports integer arithmetic on 8 bit, 16 bit and 32 bit integers. It has support for both signed and unsigned arithmetic, although divide and modulo are only implemented for unsigned integers. Unlike standard Python, you must specify the width of your integer variables and there is no support for integers that do not fit within a 32 bit data type. The following operations are supported for unsigned integers: `+` (addition), `-` (subtraction), `*` (multiplication), `/` (division), `%` (modulo), `&` (bitwise and), `|` (bitwise or), `~` (bitwise not), `^` (bitwise xor), `<<` (logical shift left), `>>` (logical shift right). Additionally, all previously listed operations except for `/` and `%` are supported for signed integers. Additionally, Python's augmented assignment operators are fully supported for all operations that are supported normally.

Integer arithmetic that causes overflow does not automatically resize the integer to a larger version so care must be taken to choose the integer data type that will adequately fit the calculations you wish to perform. Do note that larger integers are slower to operate on due to the MiniDragon being an 8 bit CPU at its core. Therefore, there is a direct trade-off between range of integers available and the speed at which calculations against those integers can be done. For the best speed, stick with 8 bit integers for everything that does not need more as most basic operations are mapped directly to CPU instructions.

Examples of various operations are as follows.

---

`a: uint8 = b + c`

 > Adds the integers `b` and `c` together and places the result into a newly-defined variable `a`. The operation will be performed with 8 bits of precision due to the destination of the expression being an 8 bit integer. If `b` or `c` are larger integers they will be truncated to 8 bits before the addition is performed.

---

`a += 5`

 > Adds 5 to the already-defined integer `a`. Note that this requires `a` to already exist since it is adding 5 to it, so `a` will have been defined with a type on a previous line.

---

`a: int16 = b - c`

 > Subtracts the value in `c` from `b` and places the result into a newly-defined variable `a`. The operation will be performed with 16 bits of precision. If `b` or `c` are larger than 16 bits, they will be truncated to 16 bits before the operation is performed. If `b` or `c` are smaller than 16 bits, they will be sign-extended to 16 bits before the operation is performed due to the fact that the result of the operation is a signed integer. If `a` was instead defined as a `uint16` then smaller integers would be zero-extended instead.

---

`a = (a + 1) & 0x3F`

 > Caculates the value of `a + 1` and then boolean ands the result against `0x3F` before assigning the result back to `a`. This effectively creates a counter that will increment `a` by `1` whenever it is called until it hits `63` where it will wrap back around to `0` on the next execution.

### String Support

MiniPy supports a string data type and basic operations on strings. Strings work similarly to their counterpart in Python and unlike `char *` style arrays in C-like languages. That is, strings are passed by value, not by reference. Assigning a string to a variable makes a copy of that string such that modifying the variable later will not affect what it was assigned from. Strings support indexing by both an integer to access the character at a specific index as well as indexing by slice in order to return a substring consisting of the characters at the beginning to the end index.

Unlike Python, MiniPy lets you assign a character to an index in a string. This is because strings are mutable in MiniPy. Note that MiniPy only supports strings up to 127 characters in length and has no support for multi-byte unicode values. There is no support for Python's `encode()` and `decode()` functions and there is no support for raw bytestrings because a MiniPy string is effectively a null-terminated bytestring. Unlike Python, each individual character in a string has the data type of `char`, not `str`. That means that performing an operation such as `string[5]` will return a `char` data type, whereas performing an operation such as `string[5:6]` will return a `str` data type.

Note that, for speed reasons, when the compiler can prove that there is no way to accidentally cause aliasing issues, strings will be represented under the hood as a reference to another string instead of a full copy. This only happens with constant strings that are assigned to from a string literal, a global constant string, a function marked as returning a constant string, or another local constant string that was assigned to from one of these categories. Functions are only allowed to be marked as returning a constant string if the value they are returning fits within one of these categories as well. This support for references under the hood extends to string function parameters that are marked as constant. In order for the compiler to guarantee correctness, functions declared as returning a constant string with `const[str]` are checked to ensure that all of their returns match the above rules. Functions which attempt to return non-constant expressions or even local constants that were derived from non-constant expressions will be flagged with a compiler error.

Examples of various operations are as follows.

---

`a: str[16] = ""`

 > Declares a string that can hold at most 16 bytes including the null terminator and initializes it to an empty string.

---

`a += b`

 > Concatenates the value of `b` to the end of an existing string `a`. If `b` is a string as well, this is equivalent to the C function `strcat(a, b)`. If `b` is a character, this appends the character to the end of the string, updating the null terminator as appropriate.

---

`ch: char = a[5]`

 > Grabs the sixth character out of the string `a` (string indexes are zero-based in MiniPy just as they are in standard Python) and assigns it to the newly declared character `ch`. Note that unlike standard Python, MiniPy character indexes are not memory safe. That means that if your string is only 3 characters long and you ask for a character at index 5 you will get a garbage result.

---

`b: str[8] = a[3:7]`

 > Declares a new string `b` and then assigns it the slice of `a` starting at index 3 and ending at index 7. Supposing `a` were to hold the value "Hello, world" then after this operation `b` will now hold "lo, ". Note that string slices are memory safe just as they are in standard Python. That means that if a string is not long enough for the slice index you should expect the result of the slice to be shorter than specified. For instance, if `a` were to hold just the string "Hello" and you were to ask for the above slice, `b` would end up containing "lo. Note that slices with no beginning and slices with no end are both supported.

---

`a = a[:5]`

 > Truncates an already-defined string `a` to just the first 5 characters. If `a` does not contain 5 characters then this has no apparent effect.

---

`l: uint8 = len(a)`

 > Calculates the length of string `a` and places the result in a newly-declared integer `l`. This is equivalent to the C function `strlen(a)`.

---

`val: str[32] = "Value: " + str(v)`

 > Converts the already-defined variable `v` to a string and concatenates it with a string constant and then assigns the result to a newly-declared string `val`. Supposing `v` was an integer holding the value `123`, you should expect that after executing this statement that `val` would contain "Value: 123". Similarly, if `v` was a boolean holding the value `True`, you should expect that after running this statement `val` would contain "Value: True".

---

`result: str[64] = f"The result of {a} added to {b} is {a + b}."`

 > Evaluates an f-string expression which references two previously-defined integer variables `a` and `b`, assigning the result to the newly-defined string `result`. Supposing `a` held the integer value `5` and `b` held the integer value of `7`, then you should expect `result` to contain "The result of 5 added to 7 is 12.". F-string expressions support all embedded expressions that MiniPy would otherwise support on a standalone line. Note that MiniPy has no support for format specifications such as `!r`.

### Boolean Support

MiniPy supports a boolean data type to represent comparison expressions. It has limited support for automatic conversion from truthy values to boolean values, specifically when non-booleans are used in `if` statements, `while` loops and conditional expressions. In the case of explicit or implicit conversion to boolean, Python's truthy rules apply to MiniPy. Integers are seen as truthy if they are non-zero, and falsey when they are zero. Strings are considered truthy if they contain one or more characters, and falsey if they are empty or zero-length. Characters are considered truthy when they represent anything other than the null byte, and falsey when they represent the null byte. Internally, `False` is represented as a byte with all bits cleared (`0`) and `True` is represented by a byte with all bits set (`255`). This only matters in the case of `peek()` and `poke()` which are documented below.

Boolean expressions are short-circuiting and evaluated from left to right. MiniPy does not support comparing different data types, such as strings against characters, or integers against booleans. Attempting to do so will result in a compile-time error on the offending line. The only exception to this is in if statement tests, while loop tests and if expression tests where a non-boolean expression is supplied but not compared against anything. In this case, MiniPy will behave the same as standard Python and evaluate the expression for "truthy" or "falsey" behavior. For integers and characters, a value is considered "truthy" if the value is non-zero, and "falsey" if the value is zero. For strings, a value is considered "truthy" if the string is non-empty (contains one or more characters that are not the null terminator) and "falsey" if the string is empty (the first character is the null terminator).

Examples of various operations are as follows.

---

`a: bool = param1 == param2`

 > Evaluates the equality check `param1 == param2` and assigns the result to the newly-created boolean variable `a`. Note that equality checks are valid only against variables and constants of the same data type. Attempting to, for instance, compare an integer against a string will result in a compile-time error. Note also that there is support for checking equality for all supported data types.

---

`a: int8 = -5 if x > 3 else 5`

 > Evaluates an if expression with the test `x > 3` and assigning the result to a newly-defined variable `a`. If `x` is indeed greater than 3, you should expect that `a` will end up with the value `-5`. If not, you should expect at `a` will contain the value `5`.

---

`a: bool = bool(someStr)`

 > Looks at an existing variable `someStr`, assumed to be a string in this case, and evaluates it for "truthy" or "falsey" contents, assigning that to the newly-created variable `a`. If the string in question is empty, then you should expect `a` to be set to `False`. Otherwise, you should expect `a` to be set to `True`.

## Control Flow Support

MiniPy supports standard `if`/`elif`/`else` statements for directing control flow with identical semantics to Python. It is perfectly valid to use a `return` statement within an if body similar to standard Python. It supports `while` statements as well, with support for the optional `else` case which is only executed if the while loop is not terminated early with a `break` statement. While loops fully support both `break` and `continue` as well as returning early from a function using the `return` statement. For statements are supported in limited context. MiniPy does not support iterators generally but provides two iteration styles for Python-style for loops. The first is the `range()` intrinsic which behaves identically to the [Python range](https://docs.python.org/3/library/functions.html#func-range) function in standard Python. The second is iterating over characters in a string. Note that much like `while` statements, `for` statements support the optional `else` clause as well as `break`, `continue` and `return` to early exit or change loop flow.

Both `if` and `while` statement expression evaluation is short-circuiting. Both `if` and `while` also support automatic coersion of truthy values. That means that instead of writing something like `if len(str) > 0:` you can instead write the more pythonic `if str:`. Note that the latter form is also faster as it does not need to evaluate the string's length and then compare it against an integer. Under the hood the compiler can optimize the second form to just check the first character of the string against the null terminator byte. Control flow statements can be nested arbitrarily and with no restrictions to depth.

Examples of various control flow statements are as follows.

---

```
var: int8 = 5
if someVal > 10:
   var += 2
```

 > This chunk of code will define a new local variable `var` which is a signed 8 bit integer. Then, given an existing variable `someVal`, if `someVal` is greater than `10` adds two to `var`. Note that `if` statements do not necessarily need an `else` statement. If omitted, the compiler will simply generate code that skips over the body of the `if` statement if the conditional is false.

---

```
if someVal and someFun(someVal):
   someVal = otherVal
```

 > This chunk of code will conditionally set the existing and previously defined `someVal` to the same value as `otherVal` as long as the `if` statement conditional is true. In this case, `someVal` can be any data type since the compiler will evaluate both parts of the `and` expression for truthiness. It can be a string, in which case the left hand side will evaluate to `True` if the string is non-empty. It can be an integer, in which case the left hand side will evaluate to `True` if the integer is non-zero. It can be a boolean which will be evaluated directly. It can be a character, in which the left hand side will evaluate to `True` if the character is not the null character. Note that the function `someFun` is only called with the value `someVal` if the left hand side evaluates to `True`. If not, the right hand side is skipped entirely since the compiler performs short circuiting on conditional expression evaluation.

---

```
local: str[8] = "hello"
count: int8 = 0
while count < 5:
    if local[count] == '!':
        break
    if local[count] == '@':
        count += 2
        continue
    count += 1
else:
    count -= 5
```

 > This chunk of code demonstrates a couple of concepts. First, it shows how to create a `while` loop with a conditional. Second, it shows that while loops can use `break` or `continue` to early exit from the loop or skip over the rest of the body of the loop and resume from the top. Third, it shows off both standard Python and MiniPy's support for the `else` case in loops. This is a lesser-known feature of Python that allows you to conditionally run code only if the loop was not exited from early. That means if a `break` statement is ever executed, then the code will jump directly past the `else` clause. If the loop exited due to the loop conditional `count < 5` becoming false, then the code will jump to the `else` body and execute the code therein. Note that just like with `if` statements, you do not need to provide an `else` statement for `while` loops. Omitting this statement is perfectly allowed.

---

```
i: uint8
j: uint8 = 0
for i in range(5):
    j += 1
```

 > This chunk of code demonstrates the standard way of creating a `for` statement in both Python and MiniPy. The `range()` intrinsic, when given a single parameter, will generate an iterator that loops through the values `0`, `1`, `2`, `3` and finally `4`. You can think of `for` statements in this format as having an equivalent C representation of `for(int i = 0; i < 5; i++)`. Note that this particular example does not show any use of a `break`, `continue`, or an `else` clause on the `for` statement itself. If the example code were to use a `continue` statement, the code would begin execution again at the top of the body of the `for` statement after incrementing the loop counter `i` and checking it against the terminating condition. These are all supported in an identical fashion to `while` statements. Note that there is one key difference between this code and standard Python code. In standard Python, the value of `i` after the loop exits will be `4` because Python is generating an actual iterator under the hood and the last value in that iterator is `4`. In MiniPy, the value of `i` after the loop exits will be `5` because MiniPy evaluates the loop iterator (which is implicitly `1` in this case) before checking the termination condition.

---

```
i: uint8
j: uint8 = 0
for i in range(1, 9, 2):
    j += 1
```

 > This chunk of code demonstrates that the `range()` intrinsic can also be used to specify a beginning value, an end value and an increment value. The `for` statement here would have the equivalent C representation of `for(int i = 1; i < 9; i += 2)`. Both standard Python and MiniPy allow you to specify a `range()` intrinsic with a single, two, or three values. In the first case, the value specified is the end value, and the compiler will create a loop for you starting at `0`, incrementing by `1` each loop, and terminating when the loop variable hits the end value. In the second case with two parameters, the compiler will generate a loop for you starting at the first value provided, incrementing by `1` each loop, and terminating when the loop variable hits the second value provided. In the third case with three parameters, the compiler will generate a loop for you starting at the first value provided, incrementing by the third value each loop, and terminating when the loop variable hits the second value provided. Variables and expressions can be used for any of the parameters to the `range()` intrinsic, but do note that both the end and increment expression will be evaluated on every iteration. Note also that `break`, `continue` and an `else` clause are all valid in any of these types of `for` loops.

---

```
someStr: str[8] = "hello":
ch: char
sum: uint8 = 0
for ch in someStr:
    sum += ord(ch)
```

 > This chunk of code demonstrates that you can use a string as an iterator for a `for` statement. The code here shows an incredibly simple checksum algorithm which simply computes the sum of all characters in the string `someStr`. The loop will iterate over each character in the string, in order, until the null terminator character is hit. Both `break` and `continue` work here as expected, as does the `else` clause. If all you need to do is access each character in a string in order without the index, this form is faster than a similar `for` statement iterating over every position and fetching the character out of the string using `someStr[index]`.

### Function Support

MiniPy supports defining functions as well as calling functions in a similar fashion to standard Python. Parameters, including strings, are passed to functions by value except in very specific cases regarding string constants. Full support for default arguments is included, so if you specify a default for a given argument you do not need to provide a value when calling the function. Similarly, support for calling functions with keyword arguments is also available. This can come in handy when you want to specifically override only some defaults for a particular function. Note that MiniPy does not support dictionaries or lists, so support for `*args` and `**kwargs` is not available.

Function calls are handled on the stack, meaning that functions are allowed to call themselves recursively. Due to the fact that strings are assigned by value, it is safe to use strings in recursive functions. All other supported data types are similarly supported for recursive functions. Due to the fact that there are no interrupts in the MiniDragon CPU, there is no support for threading or and multi-processing support. Therefore, functions do not need to worry about reentrancy.

Examples of various function definitions and their calls are as follows.

---

```
def foo(p1: int8, p2: int8) -> int8:
    return p1 * 2 + p2

def main() -> void:
    local: int8 = foo(5, 7)
```

 > Defines a function `foo` which takes two parameters, both specified as 8 bit signed integers. The function itself is simply, evaluating the expression `p1 * 2 + p2` and returning that to the caller. Defines a function `main` which calls function `foo` with two parameters as required, assigning the result of the function to a newly-defined variable `local`. After executing this, you should expect that the value of `local` is `17`. If you were to try to call `foo` with more than or less than two parameters you should expect a compile-time error on the offending line.

---

```
def foo(p1: int8, p2: int8) -> int8:
    return p1 * 2 + p2

def main() -> void:
    local: int8 = foo(p2=5, p1=7)
```

 > Defines an identical function to the previous example, but shows off the function being called using named parameters in `main`. Since parameter names were used, the compiler will assign the values according to name instead of position. You should expect that the value of `local` is `19` after execution. Note that it is a compile-time error to specify a parameter both positionally and in a named parameter, to specify the same named parameter multiple times, or to leave out a parameter that does not have a default. Note that you are allowed to mix and match positional and named parameters as you see fit, but named parameters must always come after all positional parameters.

---

```
def foo(p1: int8, p2: int8 = 9) -> int8:
    return p1 * 2 + p2

def main() -> void:
    local1: int8 = foo(3)
    local2: int8 = foo(4, 6)
    local3: int8 = foo(7, p2=8)
```

 > Defines a function `foo` that has an identical body to the previous two examples, but provides a default value for the parameter `p2`. Note the three calling styles that used when invoking `foo` inside `main`. The first invocation leaves out the second parameter entirely. The compiler will substitute the default which is `9` in this case, assigning the result of `15` to `local1`. The second invocation supplies a value for both `p1` and `p2` positionally so the compiler will override the default, assigning the result of `14` to the variable `local2`. In the third invocation the caller is mixing positional and named arguments. The result of `22` will be assigned to the variable `local3`.

---

```
def lut(key: uint8) -> const[str]:
    if key == 0:
        return "foo"
    elif key == 1:
        return "bar"
    else:
        return "baz"

def op(prefix: const[str], key: uint8) -> str[16]:
    return prefix + " " + lut(key)

def main() -> void:
    local: str[32] = op("val:", 1)
```

 > Defines a function `lut` which operates as a look-up for a particular key. Note that the function is typed as returning a `const[str]`. This is allowed because the compiler can see that all valid return paths return a constant string. If the function were to return a local variable or the result of an expression, the compiler would not allow the function to be typed as `const[str]`. Defines a second function `op` which takes a `prefix` string and a `key` integer and computes a string concatenation with said prefix and the result of the `lut` function call. Note that since the function is returning the result of an expression, the function return must have a size specifier for the string. This is similar to how non-constant string variables must have a maximum size specification. Finally, the code is executed in main, assigning the result of `op` to the `local` string. Upon executing this code, you should expect the value of `local` to be `"val: bar"`.

### Global Variable Support

MiniPy's support for non-function execution is extremely minimal. Essentially the only thing you're allowed to do at the top level is import identifiers from another module or define a function. Arbitrary top-level code is not supported and will generate a compiler error on the offending line. However, defining global constants and global variables is supported. These work similarly to standard Python in that you can always access the value of a global variable that is in your scope without defining it as long as the name isn't shadowed by a local variable. Writing to a global variable requires declaring that you are accessing a global variable with the `global` keyword. Aside from that, globals are accessed in an identical manner to local variables and behave identically.

Initializing global constants is required since MiniPy requires that to use the `const[]` modifier you do not attempt to modify the variable once it has been declared. Initializing global variables is not required, but it is recommended to do so. Unlike local variables where the compiler will generate an error on the offending line if you attempt to use a variable that has been declared but not initialized, global variables have no protection against their use before initialization. Both global constants and global variables can only be initialized with a constant expression. That is, if the value of the expression is known at compile-time, the initialization is valid. This can include other global constants that were defined previously but not global constants that were imported from other modules.

Examples of various global variable uses are as follows.

---

```
GLOBAL_CONST: const[str] = "Hello, world!"
global_var: int8 = -37
```

 > Defines two global variables. The first one, `GLOBAL_CONST`, is a constant, meaning it cannot be mutated or overwritten after defining it. the second one, `global_var`, is non-constant and initialized to the value `-37`. Both can be read freely from any function in the same module. Both can be imported as identifiers to other modules and then used freely inside functions fonud in those other modules.

---

```
_running: bool = False

def setRunning(newVal: bool) -> None:
    global _running
    _running = newVal

def getRunning() -> bool:
    return _running
```

 > Defines a global variable `_running` that uses Python's convention of prefixing variables and functions that should not be imported with an underscore. Note that the compiler will freely let you import a function or global variable starting with an underscore but it is considered bad form. Also defines a setter and a getter function that allows code to call a function to set the value or get the value of `_running`, presumably designed as the public interface to this global variable. Notice that the setter function `setRunning` requires you to declare that you intend to use the global variable `_running` using the `global` declaration. Failing to do so will cause the compiler to assume you meant to assign to a local variable which has not been defined yet. The getter function `getRunning` follows Python's convention where reading the value of a variable first looks in the local stack and then falls back to globally defined variables.

## Compiler Intrinsics

Standard Python has support for a plethora of built-in functions. MiniPy replicates support for only a limited subset of these functions. Additionally, it adds a few intrinsics of its own. All supported intrinsics are documented here. The standard Python built-ins which MiniPy supports are listed below. In general, these should behave the same as their standard Python counterparts unless documented otherwise. For standard Python documentation of these intrinsicts, please see the [Built-In Functions](https://docs.python.org/3/library/functions.html)
documentation.

---

`len(str)`

 > Given a string literal or variable as its only argument, returns the length of the string in characters (not including the null terminator) as a `uint8`. Note that this only works with strings up to 127 characters long as that is the supported length limit of strings in MiniPy

---

`str(obj)`

 > Given any supported data type, returns a string conversion of that data type. Supports integers, booleans, characters and other strings. For strings and characters, the literal value as a string will be returned. For integers, the conversion of that integer to a decmial number including a negative sign will be returned. For booleans, the string "True" or "False" will be returned depending on the value of the boolean.

---

`int(obj)`

 > Given a string, integer or boolean, returns an integer conversion of that data type. For Strings, the conversion to an integer including a potential negative sign will be returned. For integers, the number passed in will be returned. For booleans, the number 1 or 0 will be returned for `True` and `False` which is identical to standard Python.

---

`abs(int)`

 > Given a signed integer, returns the absolute value of that signed integer at the same integer width.

---

`bool(obj)`

 > Given any supported data type, returns a boolean representing the truthiness of the data type passed in. For strings, returns `True` for any string that is not zero-length, and `False` for empty or zero-length strings. For integers, returns `True` for all nonzero numbers and `False` for zero. For booleans, returns the value passed in. For characters, returns `True` for all characters that are not the null byte, and `False` for the null byte.

---

`chr(int)`

 > Given an integer, returns the character equivalent of that integer.

---

`ord(char)`

 > Given a character, returns the integer equivalent of that character.

---

`hex(int)`

 > Given an integer, returns a string representing the hexidecimal value of the integer, including the `0x` prefix, mirroring standard Python.

---

`min(int, int)`

 > Given two integers, returns whichever one is smallest in magnitude.

---

`max(int, int)`

 > Given two integers, returns whichever one is the largest in magnitude.

---

`range(int, int=None, int=None)`

 > Given one, two or three integers, returns an interator useful in `for` statements. Note that this is only supported in `for` statements since MiniPy has no support for iterables otherwise. For more details on the parameters, please see Python's [range](https://docs.python.org/3/library/functions.html#func-range) documentation.

Additionally, MiniPy specifies a few intrinsics of its own. The MiniPy specific intrinsics are documented below.

---

`peek(addr, length=None)`

 > Given a 16 bit integer interpreted as a raw memory address, peek at that memory address and return the value contained therein. The return type of peek is dependent on the variable being assigned to in the expression that it is used in. When assigning to an 8 bit integer, peek will read the byte at the memory location and return that as an 8 bit integer. When assigning to a 16 bit integer, peek will read the two bytes at the memory address and subsequent memory address and interpret and return the value as a big-endian 16 bit integer. When assigning to a 32 bit integer, peek will read the four bytes at the memory address and subsequent three memory addresses and interpret and return the value as a big-endian 32 bit integer. When assigning to a character, peek will read the byte at the memory address and return it as a character. When assigning to a boolean, peek will read the byte at the memory address and return `True` for a non-zero byte and `False` for a zero byte. When assigning to a string, peek will perform a string copy starting at the given memory address until it encounters a null terminator byte. Optionally, for strings, you can specify a second parameter as an integer which will be treated as the length to copy. Strings longer than that will be truncated when the length limit is hit, and strings equal to or less than that length will be copied in their entirity.

---

`poke(addr, obj)`

 > Given a 16 bit integer interpreted as a raw memory address and a value to store, stores that value at that address. For integers, stores the value starting at that address in big-endian. For 8 bit integers, this only modifies the byte at the specified address. For 16 bit integers, this modifies the specified and subsequent byte. For 32 bit integers, this modifies the specified and subsequent three bytes. For characters, stores the character as a byte at the address specified. For booleans, stores either 0 or 255 depending on whether the value is `False` or `True`. For strings, copies the specified string starting at the memory address until the end of the string is reached. Note that the null byte is copied in this instance.

---

`cast(type, obj)`

 > Given a valid MiniPy type and an object, cast that object to that type. Currently only supports casting `uint16` to `str` and `str` to `uint16`. When performing a cast from a string to an integer, the resulting value that is returned is the memory address that the string resides at. When performing a cast from an integer to a string, the resulting value is a string that points at the given memory address.

---

`fixed(value, fracbits=8)`

 > Given an integer or floating point value and an optional fractional bits, converts that value to a fixed point integer that represents the decimal approximation of the floating point value. Note that in MiniPy, fixed point integers are always 32 bits wide.

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

---

`from hardware.serial import serial_init, serial_clear, serial_send`

 > Looks for the identifiers `serial_init`, `serial_clear` and `serial_send` in the module which implements `hardware.serial` and makes them available in the current module. That module could be the relative file `hardware/serial.py` relative to the module performing the import, or it could be the relative file `hardware/serial.py` existing in a library directory specified to the compiler with `-l` or `--lib`.

---

`def func(param1: int16, param2: int32) -> extern[bool]: ...`

 > Defines a function prototype for `func` which takes two parameters and returns a boolean. Note the `extern[]` modifier as well as the ellipses (`...`). The compiler will emit code that refers to the global label `func` which should be implemented in an assembly file and linked into the final build. Note also that it is possible to declare functions as extern instead of importing them from other modules. It is heavily recommended to not do this because prototypes could get out of sync with the actual function implementation. If this happens, the compiler will generate incorrect code to call the function and you will most likely end up with a crash. So, it's best to leave `extern[]` functions and variables for when you need to implement something in pure assembly and reference it from within MiniPy code.

## Included Libraries

MiniPy ships with a stdlib that was implemented in assembly as well as several libraries of functions implemented in MiniPy itself. Note that under most circumstances you should not need to call the assembly stdlib directly as the functionality has been mapped onto standard Python operations. However, if you so desire, you can call the functions directly in your code. Those functions aren't documented here because they're meant to be internal to the compiler. Instead, libraries that are intended to be used are documented here.

### sys

MiniPy has extremely limited support for Python's `sys` module. Absolutely no functions are supported but if you `import sys` you will have access to a few constants provided by the compiler that you can use in your code. Note that there is currently no support for `from sys import X` style importing of the pieces of `sys` that are supported. The bits of `sys` that are supported are documented below.

---

`sys.byteorder`

 > A string constant that is always equal to `big`, representing that MiniPy byte order is big-endian.

---

`sys.hexversion`

 > A uint32 integer that is set to the current version of the compiler, in the form of `0xAABBCCCC` where `AA` is an 8 bit major version, `BB` is an 8 bit minor version, and `CCCC` is a 16 bit point version. This should not be used for displaying version information, but can be used in integer comparisons if you need to switch on compiler version.

---

`sys.maxsize`

 > An integer that is set to the maximum size of a signed integer in MiniPy. This is the constant `2^31 - 1`.

---

`sys.maxunicode`

 > An integer that is set to the maximum supported unicode codepoint. Since MiniPy only deals with extended ASCII characters in strings and has no unicode support, this is set to `0xFF` or `255`.

---

`sys.platform`

 > A string constant that is always equal to `minidragon`. This can be used in code you intend to be semi-portable to determine if you're running under MiniPy or on a standard Python distribution.

---

`sys.version`

 > A string constant that is set to the current version of the compiler, in the form of `A.B.C` where `A` is the major version, `B` is the minor version and `C` is the point version. This can be used to display the version of the toolchain a particular program was compiled with.

### hardware.serial

A library for interacting with a VT-100 terminal over a serial port attached to a R6551AP serial chip in peripheral slot 0. This is the intended serial chip and peripheral slot number for the serial port on the actual MiniDragon as built. It is where keyboard input as well as text output is handled for interactive programs. To use any of the following functions, import them using a statement in the form of `from hardware.serial import bla` where `bla` is the function that you wish to support. Note that in order to successfully compile, the compiler will need to know where to find this library. So, you should use the compiler option `-lib /path/to/lib/` to point the compiler at the `lib/` directory included at the root of this repo.

---

`serial_init() -> void`

 > Initializes the serial chip so that it is ready to communicate with a VT-100 at 9600 baud, 8 bits, no parity bit, a single stop bit, and with XON/XOFF software control flow enabled. If you wish to use any serial features you must call this early in your program init, preferrably near the top of your `main()` function.

---

`serial_send_byte(byte: const[uint8]) -> void`

 > Send a single byte over the wire to the remote VT-100. Note that this takes a byte, not a character. To cast a character to a byte you can use the built-in `ord()` which works identically to its counterpart in standard Python. Note that while this function will wait until the transmit buffer is empty before sending the byte, it does not handle any XON/XOFF control flow from the remote side. So, this should be seen as an incredibly low level direct-access function to send a byte as soon as it is possible to do so.

---

`serial_has_byte() -> bool`

 > Returns a boolean `True` if there is a byte waiting in the receive buffer of the serial chip, or `False` if there is not. To receive that byte, call `serial_recv_byte()`.

---

`serial_recv_byte() -> uint8`

 > Receives a single byte from the serial buffer. If a byte is ready to be received, returns that byte. If not, then the behavior of this function is undefined and you will get whatever the R6551AP wants to return when reading a buffer that has no byte in it. This is likely to be a null byte, but the datasheet does not specify. Note that this does not handle any XON/OFF control flow so if the VT-100 has requested to turn off transmit you may read an `0x11` or `0x13` from this. So, this should be seen as an incredibly low level direct-access function to receive a byte should there be one to receive. To cast a byte to a character you can use the built-in `chr()` which works identically to its counterpart in standard Python.

---

`serial_clear() -> void`

 > Sends the appropriate VT-100 escape sequence to clear the screen, reset all text decoration and move the cursor to the top left position.

---

`serial_normal() -> void`

 > Sends the appropriate VT-100 escape sequence to turn off any text decoration previously requested.

---

`serial_bold() -> void`

 > Sends the appropriate VT-100 escape sequence to turn text bolding on. Subsequent text sent to the VT-100 will appear bold along with any other active decorations.

---

`serial_underline() -> void`

 > Sends the appropriate VT-100 escape sequence to turn text underlining on. Subsequent text sent to the VT-100 will appear underlined along with any other active decorations.

---

`serial_reverse() -> void`

 > Sends the appropriate VT-100 escape sequence to turn text reverse printing on. Subsequent text sent to the VT-100 will appear with the foreground and background colors reversed along with any other active decorations.

---

`serial_send(data: const[str]) -> void`

 > Sends a null-terminated string to the VT-100. This could include escape sequences or any text for display. Note that this function handles polling the remote VT-100 for XON/XOFF control flow so that it does not overwhelm a remote terminal. It also swallows any incoming escape sequences sent by the terminal. It does this because in order to detect control flow bytes it must read from the remote side. If it gets an escape sequence it must read until the sequence is done otherwise code that reads after calling `serial_send()` could end up reading part of an escape sequence and corrupting user input.

---

`serial_recv(echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> str`

 > Receives a null-terminated string from the VT-100. Reads from the VT-100, swallowing escape sequences and buffering any user input until the return key is pressed. Supports erasing previously-input text using the backspace key. Also supports handling XON/XOFF style control flow in the case that the VT-100 has sent us a request to stop transmitting. By default the input that is typed will be echoed to the terminal much in the same way typing on the command-line works on a modern computer. To turn that off, set the `echo_input` parameter to `False` instead of the default `True`. To echo the mask character `*` instead of the typed character, turn on `mask_input` by setting the parameter to `True` instead of the default `False`. Note that this setting has no effect if `echo_input` is `False`. If you wish to allow empty string input (pressing enter without typing anything), you can set `allow_empty` to `True`. Otherwise, the function will only let the user continue once at least one character has been typed before pressing enter.

---

`serial_input(prompt: const[str], echo_input: bool = True, mask_input: bool = False, allow_empty: bool = True) -> str:`

 > Display the prompt string `prompt` to the VT-100 before waiting for the user to enter some text and press enter. Upon pressing enter a newline will be sent to the VT-100 to place the cursor on the next line. The optional parameters `echo_input`, `mask_input` and `allow_empty` have the same functionality and default values as in `serial_recv()`.

### conversion.fixed

A library for converting fixed point decimal numbers to strings and strings to fixed point decimal numbers. MiniDragon and MiniPy both lack any floating point support and generally only work with integers. However, floating point decimals are not the only system. Fixed point decimal numbers are employed to allow working with decimal numbers in a way that is possible with the speed and hardware limitations of the MiniDragon. Along with the `fixed()` intrinsic that allows you to define decimal constants in code easily, the conversion library allows you to accept user input and convert it to a fixed point number suitable for performing math against. It also allows you to take a fixed point number and convert to the approximate decimal representation for displaying to a user.

Note that there is no math library for working with fixed point decimal numbers. That's because the math for fixed point decimal numbers works out to be compatible with existing integers. For more information, please read up on [Fixed Point Arithmetic](https://en.wikipedia.org/wiki/Fixed-point_arithmetic). However, non-bitwise math should generally work out. For instance, to add two fixed-point numbers stored in `a` and `b` with the same `fracbits` together, one would simply perform the expression `a + b`. The same thing works for subtraction, where you would perform `a - b`. Negating numbers works as expected, and negative numbers input by the user will be in the correct form for arithmetic to work out. Multipliciation is similar to how you learned to multiply on paper. The result of any multiplication needs to be shifted right by `fracbits`. So, to multiply two numbers, you would perform an expression similar to `(a * b) >> fracbits`. Division works in reverse, where you would shift left by the number of fracbits. Tricks for multiplying or dividing by a power of two using a shift operation still work the same. Note that there are concerns with loss of precision when multiplying and dividing, as well as the possibility of multiplying and dividing numbers with different `fracbits` as long as you manage your final shift correctly. For details, please read up on the wikipedia link above.

To use any of the following functions, import them using a statement in the form of `from conversion.fixed import bla` where `bla` is the function that you wish to support. Note that in order to successfully compile, the compiler will need to know where to find this library. So, you should use the compiler option `-lib /path/to/lib/` to point the compiler at the `lib/` directory included at the root of this repo.

---

`strtofixed(val: const[str], fracbits: uint8 = 8) -> int32`

 > Given a string that represents an integer or decimal number, conver it to a fixed width integer suitable for performing math against. Note that much like the `fixed()` intrinsic, this defaults to 8 fractional bits of precision, allowing you to represent down to `1/256` of decimal. If you wish to change this, you can specify another value for the `fracbits` parameter. Note that fixed width decmials do not carry any metadata with them so neither the compiler nor the conversion library will warn you if you try to convert a number with one `fracbits` value and then display it with another `fracbits`.

---

`fixedtostr(val: int32, precision: uint8, fracbits: uint8 = 8) -> str`

 > Given a fixed point decimal number and a precision, converts that number to a string suitable for display to a user. The `precision` argument is the number of digits after the decimal place. Valid values are `0`-`6` inclusive. Note that this function will round the number before display so that the rendered display is as close to correct as possible. So, if you had the number `3.75` or `3.9` and converted it to a string with `precision` set to `0`, you should expect to get back a string with the value `"4"`. Similarly if you had the number `3.01` and converted it with a `precision` of `1` you should expect to get a string back with the value `"3.0"`. If instead your number was `3.09` and you specified the same precision, you'd instead expect to get back a string with the value `"3.1"`. The same warning about `fracbits` applies. It is your responsibility to ensure that you use the same `fracbits` for all conversions and `fixed()` intrinsics if you wish for the converted numbers to be correct.

## Application Binary Interface

Since the MiniDragon ISA is stack-based with an accumulator, it should come as no surprise that function parameters, local variables, the function return and the return address are placed onto the stack. If you are looking to write functions in assembly which interop with MiniPy code it is important to respect the ABI otherwise you will most likely get a crash from stack corruption. The easiest way to conform to the interface for a given function is to simply let the compiler generate the function stub for you. Define the function with its parameters and return in a module, return a dummy value, compile it, and copy the skeleton out of the assembly listing.

The MiniDragon CPU uses a standard stack that starts at the top of memory and grows down. A push operation will decrement the PC register and then store the value at the memory location pointed at by PC. A pop operation will load the value from the memory location pointed at by PC and then increment the PC register. Function parameters are always provided on the stack even when they could fit in the A, U or V registers. They are pushed onto the stack in the order that they appear in the function definition. When a function is called, after the compiler pushes all of the parameters onto the stack, the actual call operation will push the address of the instruction after the call onto the stack as a big-endian 16 bit address and then jump to the first byte of the function. That means upon entering a function you should expect the PC register to point at the first byte of the return address in memory with the second byte in the next memory address.

It is the function's responsibility to restore all registers to their previous state upon exiting a function. The compiler does not recognize any temporary registers that are considered dirty after a function call. That means if you use a register in your function, you're required to push the value of that register onto the stack at the beginning of your function and pop the value off of the stack just before returning. This requirement exists for the `A`, `U`, `V` and `SPC` registers but does not exist for the `PC` or `IP` registers since those are expected to be modified by executing the function. Just about every useful function will end up clobbering the `A` register so it is a safe bet to assume you will be saving this register when writing any meaningful function.

When leaving a function, a ret operation is used to pop the return address from the stack and jump to it. This means that when you leave a function you are expected to have the PC register pointing at the first byte of the return address on the stack. When that return address is popped, the PC will be incremented by 2 and should point at the first byte of the return value. The calling code will expect to pop that value from the stack which should return the PC register to the location that it pointed at before any function parameters were pushed onto the stack. That means that it is the called function's responsibility to move the return address and return value when appropriate. This will be necessary when the function parameters take more space on the stack than the return value. Since the calling code expects the parameters to be "consumed" by the called function it will not attempt to pop the parameters off the stack when execution is returned to it after the ret operation.

Note that in cases where the return value takes more space on the stack than the parameters the compiler will insert padding bytes onto the stack so that the called function does not need to relocate the return pointer down the stack to make room for the return value. If the length of all parameters exactly equals or surpasses the size of the return value (or the function is a `void` return) then no padding will be inserted. If you do not want this and you are willing to relocate the return value and return pointer on the stack even when padding bytes could be inserted for you, you can use the `nopad[]` modifier on the function's return type. Using `nopad[]` will instruct the compiler not to insert padding bytes under any circumstance and you will be responsible for moving the return pointer as well as locating the return value on the stack manually.

Examples of functions as well as both their just-after-call and their just-before-return stack layout are shown below. An arbitrary stack address of `0xBEE5` has been chosen as the location of `PC` just prior to the function parameters being pladed onto the stack. The stack is presented where the highest value on the screen is also the highest memory address.

---

`def fun() -> void: ...`

The stack on the first instruction of the function as well as the stack just before returning looks like the following. `PC` should be set to `0xBEE3` both in the first instruction and just prior to returning from the function.

| Memory Location | Description                 |
| --------------- | --------------------------- |
| `0xBEE4`        | low byte of return address  |
| `0xBEE3`        | high byte of return address |

---

`def fun(p1: int8, p2: int16) -> void: ...`

The stack on the first instruction of the function looks like the following. Note that `PC` should be set to `0xBEE0` when your function starts executing.

| Memory Location | Description                 |
| --------------- | --------------------------- |
| `0xBEE4`        | parameter p1                |
| `0xBEE3`        | low byte of parameter p2    |
| `0xBEE2`        | high byte of parameter p2   |
| `0xBEE1`        | low byte of return address  |
| `0xBEE0`        | high byte of return address |

You are responsible for making sure the stack looks like the following before returning by moving the return address. Note that `PC` should point to `0xBEE3` just prior to returning.

| Memory Location | Description                 |
| --------------- | --------------------------- |
| `0xBEE4`        | low byte of return address  |
| `0xBEE3`        | high byte of return address |

---

`def fun() -> int8: ...`

The stack on the first instruction of the function looks like the following. Note the padding byte the compiler inserts so you have room for the return value. Note that `PC` should be set to `0xBEE2` when your function starts executing.

| Memory Location | Description                      |
| --------------- | -------------------------------- |
| `0xBEE4`        | padding byte for function return |
| `0xBEE3`        | low byte of return address       |
| `0xBEE2`        | high byte of return address      |

The stack should look like the following just before returning. Note that `PC` should point to `0xBEE2` just before executing the return instruction.

| Memory Location | Description                 |
| --------------- | --------------------------- |
| `0xBEE4`        | function return value       |
| `0xBEE3`        | low byte of return address  |
| `0xBEE2`        | high byte of return address |

---

`def fun() -> nopad[int16]: ...`

The stack on the first instruction of the function looks like the following. Note that the compiler was told not to insert padding, so you are responsible for relocating the return address to make room for the function return. Note that `PC` should be set to `0xBEE3` when your function starts executing.

| Memory Location | Description                      |
| --------------- | -------------------------------- |
| `0xBEE4`        | low byte of return address       |
| `0xBEE3`        | high byte of return address      |

The stack should look like the following just before returning. You are responsible for moving the return address to make room for the return value. Note that `PC` should point to `0xBEE1` just before executing the return instruction.

| Memory Location | Description                     |
| --------------- | ------------------------------- |
| `0xBEE4`        | function return value low byte  |
| `0xBEE3`        | function return value high byte |
| `0xBEE2`        | low byte of return address      |
| `0xBEE1`        | high byte of return address     |

## Compiler Optimizations

Regardless of whether the optimize code flag has been passed to the compiler, the compiler will attempt to evaluate any constants found in the code it is compiling. That means if you have an expression whose value is known at compile-time, the compiler will not emit code to calculate that expression. Instead, the value of that expression as calculated at compile time will be inserted into the compiled assembly listing instead. The compiler is aware of global and local constants which are known at compile time in its evaluation of whole or partial expressions that can be optimized to a single value.

Additionally, when the compiler has been instructed to do so with the optimize flag (`-z` or `--optimize`) it will make passes over the assembly that it produces until it can no longer find optimizations to perform. This usually results in code that is smaller and runs faster but has the potential to accidentally emit incorrect code. Care has been taken to only perform optimizations that are provably safe and do not alter the semantics of the code at all. However, since compiler optimization passes are effectively pattern matching heuristics, it is possible that the compiler may get things wrong. The compiler will look for things such as redundant loads and stores, redundant stack moving operations, groups of instructions that are performed simply to check the zero or carry flag which can be reduced to equivalent smaller groups, conditional jumps based on constants and redundant stack operations when immediate operations could be substituted.
