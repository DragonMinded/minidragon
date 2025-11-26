all: helloworld.bin fixedpoint.bin bootrom.bin

# Runtime library.
RUNTIME += lib/runtime/init.S
RUNTIME += lib/runtime/start.S
RUNTIME += lib/runtime/const.S
RUNTIME += lib/runtime/cart.S
RUNTIME += lib/runtime/data.S
RUNTIME += lib/runtime/heap.S
RUNTIME += lib/hardware/hwregs.S

# Math library.
STDLIB += lib/math/abs.S
STDLIB += lib/math/add.S
STDLIB += lib/math/cmp.S
STDLIB += lib/math/divide.S
STDLIB += lib/math/multiply.S
STDLIB += lib/math/neg.S
STDLIB += lib/math/shift.S

# String library.
STDLIB += lib/string/strcat.S
STDLIB += lib/string/strcpy.S
STDLIB += lib/string/strlen.S
STDLIB += lib/string/strcmp.S

# Conversion library.
STDLIB += lib/conversion/itoa.S
STDLIB += lib/conversion/atoi.S
STDLIB += lib/conversion/hex.S

# Bootrom sources.
BOOTROM_SRCS += lib/hardware/serial.S
BOOTROM_SRCS += lib/hardware/serial.py
BOOTROM_SRCS += lib/hardware/cartridge.S
BOOTROM_SRCS += lib/hardware/cartridge.py
BOOTROM_SRCS += lib/conversion/fixed.py
BOOTROM_SRCS += bootrom/main.py

# Hello world sources.
HELLOWORLD_SRCS += lib/hardware/serial.S
HELLOWORLD_SRCS += lib/hardware/serial.py
HELLOWORLD_SRCS += bootrom/helloworld.py

# Fixed point test sources.
FIXEDPOINT_SRCS += lib/hardware/serial.S
FIXEDPOINT_SRCS += lib/hardware/serial.py
FIXEDPOINT_SRCS += lib/conversion/fixed.py
FIXEDPOINT_SRCS += bootrom/fixedtest.py

# Magic rule maker for above sources to map to various files.
BOOTROM_JUMPTABLE += bootrom/jumptable.S
BOOTROM_INITS := $(patsubst %.py, build/%.init.S, $(filter %.py, ${BOOTROM_SRCS}))
BOOTROM_DATAS := $(patsubst %.py, build/%.data.S, $(filter %.py, ${BOOTROM_SRCS}))
BOOTROM_CODES := $(patsubst %.py, build/%.code.S, $(filter %.py, ${BOOTROM_SRCS}))
BOOTROM_CODES += $(filter %.S, ${BOOTROM_SRCS})

HELLOWORLD_INITS := $(patsubst %.py, build/%.init.S, $(filter %.py, ${HELLOWORLD_SRCS}))
HELLOWORLD_DATAS := $(patsubst %.py, build/%.data.S, $(filter %.py, ${HELLOWORLD_SRCS}))
HELLOWORLD_CODES := $(patsubst %.py, build/%.code.S, $(filter %.py, ${HELLOWORLD_SRCS}))
HELLOWORLD_CODES += $(filter %.S, ${HELLOWORLD_SRCS})

FIXEDPOINT_INITS := $(patsubst %.py, build/%.init.S, $(filter %.py, ${FIXEDPOINT_SRCS}))
FIXEDPOINT_DATAS := $(patsubst %.py, build/%.data.S, $(filter %.py, ${FIXEDPOINT_SRCS}))
FIXEDPOINT_CODES := $(patsubst %.py, build/%.code.S, $(filter %.py, ${FIXEDPOINT_SRCS}))
FIXEDPOINT_CODES += $(filter %.S, ${FIXEDPOINT_SRCS})

# Rule to convert any python file to its output init/data/code sections.
build/%.init.S build/%.data.S build/%.code.S: %.py
	@mkdir -p $(dir $@)
	./compiler --lib lib/ --optimize -o build/$*.code.S -d build/$*.data.S -i build/$*.init.S $^

build/bootrom_listing.S: $(STDLIB) $(RUNTIME) $(BOOTROM_JUMPTABLE) $(BOOTROM_INITS) $(BOOTROM_DATAS) $(BOOTROM_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(BOOTROM_JUMPTABLE) >> $@
	cat $(BOOTROM_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(STDLIB) >> $@
	cat $(BOOTROM_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/cart.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(BOOTROM_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

build/helloworld_listing.S: $(STDLIB) $(RUNTIME) $(HELLOWORLD_INITS) $(HELLOWORLD_DATAS) $(HELLOWORLD_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(HELLOWORLD_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(STDLIB) >> $@
	cat $(HELLOWORLD_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/cart.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(HELLOWORLD_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

build/fixedpoint_listing.S: $(STDLIB) $(RUNTIME) $(FIXEDPOINT_INITS) $(FIXEDPOINT_DATAS) $(FIXEDPOINT_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(FIXEDPOINT_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(STDLIB) >> $@
	cat $(FIXEDPOINT_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/cart.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(FIXEDPOINT_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

# Rule to convert any prefixed listing file to its associated bin/sym files.
%.bin %.sym: build/%_listing.S
	./assembler \
		--origin 0x0000 \
		--size 0x7800 \
		--destination $@ \
		--generate-symbols \
		--symbol-file $(@:bin=sym) \
		$^

.PHONY: jumptable
jumptable: bootrom.bin
	cat bootrom.sym | grep "jumptable_" | grep -v "jumptable_end" | sed 's/jumptable_//' > cartridge/lib/bootrom.sym
	cp bootrom.bin cartridge/lib/bootrom.bin

.PHONY: clean
clean:
	rm -rf build
	rm -rf bootrom.bin
	rm -rf bootrom.sym
	rm -rf helloworld.bin
	rm -rf helloworld.sym
	rm -rf fixedpoint.bin
	rm -rf fixedpoint.sym
