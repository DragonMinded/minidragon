# Some configurability to move the Makefile around
# Project root directory where the compiler is found
ROOT_DIR := ../..
# Where the Python tools live, relative to this Makefile
TOOLS_DIR := $(ROOT_DIR)/core
# Assembler libraries
LIB_DIR := $(ROOT_DIR)/lib
# Where the ROM Python sources live, relative to this Makefile
SRC_DIR := roms/bootrom
# Local build/output directory (kept relative to this Makefile)
BUILD_DIR := build

all: bootrom.bin

# Math library.
LIBS += $(LIB_DIR)/math/abs.S
LIBS += $(LIB_DIR)/math/add.S
LIBS += $(LIB_DIR)/math/cmp.S
LIBS += $(LIB_DIR)/math/divide.S
LIBS += $(LIB_DIR)/math/multiply.S
LIBS += $(LIB_DIR)/math/neg.S
LIBS += $(LIB_DIR)/math/shift.S

# String library.
LIBS += $(LIB_DIR)/string/strcat.S
LIBS += $(LIB_DIR)/string/strcpy.S
LIBS += $(LIB_DIR)/string/strlen.S
LIBS += $(LIB_DIR)/string/strcmp.S

# Conversion library.
LIBS += $(LIB_DIR)/conversion/itoa.S
LIBS += $(LIB_DIR)/conversion/atoi.S
LIBS += $(LIB_DIR)/conversion/hex.S

# Main startup.
SRCS += main.py

# Hardware drivers.
SRCS += serial.py

INITS = $(patsubst %.py, $(BUILD_DIR)/%.init.S, ${SRCS})
DATAS = $(patsubst %.py, $(BUILD_DIR)/%.data.S, ${SRCS})
CODES = $(patsubst %.py,  $(BUILD_DIR)/%.code.S, ${SRCS})

$(BUILD_DIR)/%.init.S  $(BUILD_DIR)/%.data.S  $(BUILD_DIR)/%.code.S: %.py
	@mkdir -p $(dir $@)
	cd $(ROOT_DIR) && python3 compiler.py \
	    --optimize \
	    -o $(abspath $(BUILD_DIR))/$*.code.S \
	    -d  $(abspath $(BUILD_DIR))/$*.data.S \
	    -i  $(abspath $(BUILD_DIR))/$*.init.S \
	    $(SRC_DIR)/$^

$(BUILD_DIR)/listing.S: $(LIBS) $(INITS) $(DATAS) $(CODES) $(LIB_DIR)/init.S $(LIB_DIR)/start.S $(LIB_DIR)/hwregs.S $(LIB_DIR)/const.S $(LIB_DIR)/data.S $(LIB_DIR)/heap.S
	@mkdir -p $(dir $@)
	cat $(LIB_DIR)/init.S > $@
	cat $(INITS) >> $@
	cat $(LIB_DIR)/start.S >> $@
	cat $(LIBS) >> $@
	cat $(CODES) >> $@
	cat $(LIB_DIR)/const.S >> $@
	cat $(LIB_DIR)/hwregs.S >> $@
	cat $(LIB_DIR)/data.S >> $@
	cat $(DATAS) >> $@
	cat $(LIB_DIR)/heap.S >> $@

bootrom.bin: $(BUILD_DIR)/listing.S
	cd $(ROOT_DIR) && python3 assembler.py \
		--origin 0x0000 \
		--size 0x7800 \
		--destination $(SRC_DIR)/bootrom.bin \
		--generate-symbols \
		--symbol-file $(SRC_DIR)/bootrom.sym \
		$(SRC_DIR)/$(BUILD_DIR)/listing.S

run: bootrom.bin
	cd $(ROOT_DIR) && python3 emulator.py $(SRC_DIR)/bootrom.bin

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
	rm -rf bootrom.bin
	rm -rf bootrom.sym
