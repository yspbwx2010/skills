// SPDX-License-Identifier: GPL-2.0
/*
 * Minimal out-of-tree GKI module: a kprobe plus a reboot notifier.
 *
 * Shows three things:
 *   1. kprobe: with CONFIG_FUNCTION_TRACER=n (android15-6.6 gki_defconfig)
 *      it is the only general way to hook an arbitrary kernel function;
 *   2. every callback prototype matches the kernel's declared type exactly
 *      (CONFIG_CFI_CLANG=y, not permissive: a mismatch is a CFI panic);
 *   3. complete error handling and teardown.
 *
 * Load:   insmod kprobe_notifier.ko probe_symbol=do_sys_openat2
 * Check:  dmesg | tail
 * Unload: rmmod kprobe_notifier
 */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/atomic.h>
#include <linux/init.h>
#include <linux/kprobes.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/notifier.h>
#include <linux/printk.h>
#include <linux/reboot.h>

/*
 * Must resolve through kallsyms (global or static), not be inlined away and
 * not be on the kprobe blacklist, or register_kprobe() fails.
 */
static char *probe_symbol = "do_sys_openat2";
module_param(probe_symbol, charp, 0444);
MODULE_PARM_DESC(probe_symbol, "kernel symbol to probe");

static atomic_long_t hit_count = ATOMIC_LONG_INIT(0);

/*
 * Must match kprobe_pre_handler_t exactly (include/linux/kprobes.h):
 *     typedef int (*kprobe_pre_handler_t)(struct kprobe *, struct pt_regs *);
 * Writing void * instead of struct pt_regs * gives a different KCFI hash;
 * if a cast hides that from the compiler, the first hit ends in
 * die("Oops - CFI").
 *
 * Runs from the BRK debug exception in atomic context: no sleeping, no
 * GFP_KERNEL. Return 0 to let the probed instruction run normally.
 */
static int kn_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
	atomic_long_inc(&hit_count);
	return 0;
}

static struct kprobe kn_kp = {
	.pre_handler = kn_pre_handler,
	/* .symbol_name is set in init because it comes from a module parameter */
};

/*
 * Must match notifier_fn_t exactly (include/linux/notifier.h):
 *     typedef int (*notifier_fn_t)(struct notifier_block *nb,
 *                                  unsigned long action, void *data);
 * Declaring action as int does not compile here (incompatible function
 * pointer type under -Werror); casting that error away panics at reboot.
 */
static int kn_reboot_cb(struct notifier_block *nb, unsigned long action,
			void *data)
{
	pr_info("reboot action=%lu, probe hits=%ld\n", action,
		atomic_long_read(&hit_count));
	return NOTIFY_DONE;
}

static struct notifier_block kn_reboot_nb = {
	.notifier_call = kn_reboot_cb,
};

static int __init kn_init(void)
{
	int ret;

	kn_kp.symbol_name = probe_symbol;

	ret = register_kprobe(&kn_kp);
	if (ret) {
		pr_err("register_kprobe(%s) failed: %d\n", probe_symbol, ret);
		return ret;
	}

	ret = register_reboot_notifier(&kn_reboot_nb);
	if (ret) {
		pr_err("register_reboot_notifier failed: %d\n", ret);
		unregister_kprobe(&kn_kp);
		return ret;
	}

	pr_info("probing %s at %p\n", probe_symbol, kn_kp.addr);
	return 0;
}

/* Only reached after a fully successful init, so undo everything. */
static void __exit kn_exit(void)
{
	unregister_reboot_notifier(&kn_reboot_nb);
	unregister_kprobe(&kn_kp);
	pr_info("unloaded, total hits=%ld\n", atomic_long_read(&hit_count));
}

module_init(kn_init);
module_exit(kn_exit);

/*
 * Must be GPL-compatible: register_kprobe()/unregister_kprobe() are
 * EXPORT_SYMBOL_GPL. register_reboot_notifier() is plain EXPORT_SYMBOL, but
 * one GPL-only import is enough to require a GPL-compatible license.
 */
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("GKI out-of-tree example: kprobe + reboot notifier with CFI-safe callbacks");
