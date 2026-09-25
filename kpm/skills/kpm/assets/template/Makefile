# Build a KernelPatch Module. Verified against KernelPatch 0.13.9.
#   export TARGET_COMPILE=aarch64-none-elf-
#   export KP_DIR=/path/to/KernelPatch      # a checkout of the KernelPatch source
#   make

ifndef TARGET_COMPILE
    $(error TARGET_COMPILE not set, e.g. export TARGET_COMPILE=aarch64-none-elf-)
endif
ifndef KP_DIR
    $(error KP_DIR not set, point it at a KernelPatch source checkout)
endif

CC = $(TARGET_COMPILE)gcc

INCLUDE_DIRS := . include patch/include linux/include \
                linux/arch/arm64/include linux/tools/arch/arm64/include
INCLUDE_FLAGS := $(foreach dir,$(INCLUDE_DIRS),-I$(KP_DIR)/kernel/$(dir))

MODULE := __NAME__
objs := module.o

all: $(MODULE).kpm

$(MODULE).kpm: $(objs)
	$(CC) -r -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDE_FLAGS) -c -O2 -fno-common -o $@ $<

.PHONY: clean
clean:
	rm -rf *.kpm
	find . -name "*.o" | xargs rm -f
