# Example Makefile for building a cartridge for the MiniDragon CPU and minicomputer layout. Assumes that you
# have installed this repository with pipx.

all: helloworld.cart

# Assumes you have installed this repository by default, change these if that's not true.
COMPILER ?= minidragon-compiler
ASSEMBLER ?= minidragon-assembler
GENERATOR ?= minidragon-generator

# Platform support. You normally won't need to mess with this.
PLATFORM += lib/runtime/init.S
PLATFORM += lib/runtime/start.S
PLATFORM += lib/runtime/data.S
PLATFORM += lib/runtime/heap.S

# Your ROM header, where you place your cartridge name and author.
PLATFORM += header.S

# ROM sources. Include any .S or .py files that are part of your cartridge here.
SRCS += main.py

# Magic rule maker for above sources to map to various files.
INITS := $(patsubst %.py, build/%.init.S, $(filter %.py, ${SRCS}))
DATAS := $(patsubst %.py, build/%.data.S, $(filter %.py, ${SRCS}))
CODES := $(patsubst %.py, build/%.code.S, $(filter %.py, ${SRCS}))
CODES += $(filter %.S, ${SRCS})

# Rule to convert any python file to its output init/data/code sections.
build/%.init.S build/%.data.S build/%.code.S: %.py
	@mkdir -p $(dir $@)
	$(COMPILER) --lib lib/ --optimize -o build/$*.code.S -d build/$*.data.S -i build/$*.init.S $^

# Rule to link your cartridge together to a final assembly listing.
build/listing.S: $(STDLIB) $(PLATFORM) $(INITS) $(DATAS) $(CODES)
	@mkdir -p $(dir $@)
	cat header.S > $@
	cat lib/runtime/init.S >> $@
	cat $(INITS) >> $@
	cat lib/runtime/start.S >> $@
	cat $(CODES) >> $@
	cat lib/runtime/data.S >> $@
	cat $(DATAS) >> $@
	cat lib/runtime/heap.S >> $@

# Rule to convert your cartridge listing to the actual cartridge name specified in all above.
%.cart: build/listing.S
	$(ASSEMBLER) \
		--origin 0x8000 \
		--size 0x4000 \
		--use-symbol-file lib/bootrom.sym \
		--destination $@ \
		$^

.PHONY: clean
clean:
	rm -rf build
	rm -rf helloworld.cart
