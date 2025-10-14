all: bootrom.bin

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

# Main startup.
SRCS += bootrom/main.py

# Hardware drivers.
SRCS += bootrom/serial.py

INITS = $(patsubst %.py, build/%.init.S, ${SRCS})
DATAS = $(patsubst %.py, build/%.data.S, ${SRCS})
CODES = $(patsubst %.py, build/%.code.S, ${SRCS})

build/%.init.S build/%.data.S build/%.code.S: %.py
	@mkdir -p $(dir $@)
	python3 compiler.py --optimize -o build/$*.code.S -d build/$*.data.S -i build/$*.init.S $^

build/listing.S: $(LIBS) $(INITS) $(DATAS) $(CODES) lib/init.S lib/start.S lib/hwregs.S lib/data.S lib/heap.S
	@mkdir -p $(dir $@)
	cat lib/init.S > $@
	cat $(INITS) >> $@
	cat lib/start.S >> $@
	cat $(LIBS) >> $@
	cat $(CODES) >> $@
	cat lib/hwregs.S >> $@
	cat lib/data.S >> $@
	cat $(DATAS) >> $@
	cat lib/heap.S >> $@

bootrom.bin: build/listing.S
	python3 assembler.py \
		--origin 0x0000 \
		--size 0x7800 \
		--destination bootrom.bin \
		--generate-symbols \
		--symbol-file bootrom.sym \
		build/listing.S

.PHONY: clean
clean:
	rm -rf build
	rm -rf bootrom.bin
	rm -rf bootrom.sym
