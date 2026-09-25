# Thin wrapper around the out-of-tree Kbuild command. Kbuild reads ./Kbuild, not this file.
#   make KERNEL_SRC=/path/to/kernel/source KERNEL_OUT=/path/to/kernel/build/output
# KERNEL_OUT must hold the full kernel build's .config and Module.symvers
# (`make Image` alone does not produce a complete Module.symvers).

ifndef KERNEL_SRC
$(error KERNEL_SRC not set: point it at the kernel source tree)
endif
ifndef KERNEL_OUT
$(error KERNEL_OUT not set: point it at the kernel build output with .config and Module.symvers)
endif

KBUILD_CMD = $(MAKE) -C "$(abspath $(KERNEL_SRC))" O="$(abspath $(KERNEL_OUT))" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
	KCFLAGS=-D__ANDROID_COMMON_KERNEL__ M="$(CURDIR)"

all:
	$(KBUILD_CMD) modules

clean:
	$(KBUILD_CMD) clean

.PHONY: all clean
