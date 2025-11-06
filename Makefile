all: helloworld.bin fixedpoint.bin bootrom.bin

# Runtime library.
RUNTIME += lib/runtime/init.S
RUNTIME += lib/runtime/start.S
RUNTIME += lib/runtime/const.S
RUNTIME += lib/runtime/data.S
RUNTIME += lib/runtime/heap.S
RUNTIME += lib/hardware/hwregs.S

# Math library.
LIBS += lib/math/abs.S
LIBS += lib/math/add.S
LIBS += lib/math/cmp.S
LIBS += lib/math/divide.S
LIBS += lib/math/multiply.S
LIBS += lib/math/neg.S
LIBS += lib/math/shift.S

# String library.
LIBS += lib/string/strcat.S
LIBS += lib/string/strcpy.S
LIBS += lib/string/strlen.S
LIBS += lib/string/strcmp.S

# Conversion library.
LIBS += lib/conversion/itoa.S
LIBS += lib/conversion/atoi.S
LIBS += lib/conversion/hex.S

# Bootrom sources.
BOOTROM_SRCS += bootrom/serial.S
BOOTROM_SRCS += bootrom/serial.py
BOOTROM_SRCS += bootrom/main.py

# Hello world sources.
HELLOWORLD_SRCS += bootrom/serial.S
HELLOWORLD_SRCS += bootrom/serial.py
HELLOWORLD_SRCS += bootrom/helloworld.py

# Fixed point test sources.
FIXEDPOINT_SRCS += bootrom/serial.S
FIXEDPOINT_SRCS += bootrom/serial.py
FIXEDPOINT_SRCS += bootrom/fixed.py
FIXEDPOINT_SRCS += bootrom/fixedtest.py

# Magic rule maker for above sources to map to various files.
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
	python3 compiler.py --optimize -o build/$*.code.S -d build/$*.data.S -i build/$*.init.S $^

build/bootrom_listing.S: $(LIBS) $(RUNTIME) $(BOOTROM_INITS) $(BOOTROM_DATAS) $(BOOTROM_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(BOOTROM_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(LIBS) >> $@
	cat $(BOOTROM_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(BOOTROM_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

build/helloworld_listing.S: $(LIBS) $(RUNTIME) $(HELLOWORLD_INITS) $(HELLOWORLD_DATAS) $(HELLOWORLD_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(HELLOWORLD_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(LIBS) >> $@
	cat $(HELLOWORLD_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(HELLOWORLD_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

build/fixedpoint_listing.S: $(LIBS) $(RUNTIME) $(FIXEDPOINT_INITS) $(FIXEDPOINT_DATAS) $(FIXEDPOINT_CODES)
	@mkdir -p $(dir $@)
	cat lib/runtime/init.S > $@
	cat $(FIXEDPOINT_INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(LIBS) >> $@
	cat $(FIXEDPOINT_CODES) >> $@
	cat lib/runtime/const.S >> $@
	cat lib/hardware/hwregs.S >> $@
	cat lib/runtime/data.S >> $@
	cat $(FIXEDPOINT_DATAS) >> $@
	cat lib/runtime/heap.S >> $@

# Rule to convert any prefixed listing file to its associated bin/sym files.
%.bin %.sym: build/%_listing.S
	python3 assembler.py \
		--origin 0x0000 \
		--size 0x7800 \
		--destination $@ \
		--generate-symbols \
		--symbol-file $(@:bin=sym) \
		$^

.PHONY: clean
clean:
	rm -rf build
	rm -rf bootrom.bin
	rm -rf bootrom.sym
	rm -rf helloworld.bin
	rm -rf helloworld.sym
	rm -rf fixedpoint.bin
	rm -rf fixedpoint.sym
