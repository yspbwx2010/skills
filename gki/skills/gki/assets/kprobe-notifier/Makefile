# Out-of-tree GKI module build (thin wrapper around Kbuild).
#   make KERNEL_SRC=/path/to/kernel/source KERNEL_OUT=/path/to/full/build/output
#   make KERNEL_SRC=... KERNEL_OUT=... clean
# KERNEL_OUT must hold the full build's .config and a complete Module.symvers
# (`make Image` alone does not produce one). Put the branch's clang first in PATH.
# Kbuild reads the Kbuild file in this directory, not this Makefile.

ifndef KERNEL_SRC
$(error KERNEL_SRC not set: path to the kernel source tree)
endif
ifndef KERNEL_OUT
$(error KERNEL_OUT not set: path to the full kernel build output (O=))
endif

.PHONY: modules clean
modules clean:
	$(MAKE) -C "$(abspath $(KERNEL_SRC))" O="$(abspath $(KERNEL_OUT))" \
		ARCH=arm64 LLVM=1 LLVM_IAS=1 KCFLAGS=-D__ANDROID_COMMON_KERNEL__ \
		M="$(CURDIR)" $@
