// SPDX-License-Identifier: GPL-2.0
/*
 * Minimal vendor hook module: registers two plain (DECLARE_HOOK) vendor hooks
 * and removes them cleanly on unload.
 *
 * Written against OGKI android15-6.6 (Linux 6.6.118, gki_defconfig, arm64).
 * Both hooks are plain tracepoints, so this module can be unloaded. Do not add
 * an android_rvh_* (restricted) hook here: restricted hooks cannot be
 * unregistered, and a module that registers one must never be unloaded.
 *
 * Both parameters default to "off", so loading the module changes nothing.
 */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/cpufreq.h>
#include <linux/module.h>
#include <linux/tracepoint.h>

/*
 * Include the hook headers only. Never #define CREATE_TRACE_POINTS: the kernel
 * already defines and exports these tracepoints (drivers/android/vendor_hooks.c).
 * Defining them again duplicates __tracepoint_* / __traceiter_*.
 */
#include <trace/hooks/cpufreq.h>
#include <trace/hooks/cpuidle.h>

static unsigned int freq_floor_khz;
module_param(freq_floor_khz, uint, 0644);
MODULE_PARM_DESC(freq_floor_khz, "Minimum resolved CPU frequency in kHz, capped at policy->max (0 = off)");

static int idle_state_cap = -1;
module_param(idle_state_cap, int, 0644);
MODULE_PARM_DESC(idle_state_cap, "Deepest cpuidle state index allowed (-1 = off)");

/*
 * Callback prototype = "void *data" followed by the hook's TP_PROTO(), exactly.
 * register_trace_*() accepts only that type. Never cast a callback to make it
 * fit: KCFI checks the indirect call at runtime and traps on a mismatch.
 *
 * Plain hooks run with preemption disabled: no sleeping, no mutexes, no
 * GFP_KERNEL allocations. Keep callbacks O(1).
 */

/*
 * TP_PROTO(struct cpufreq_policy *policy, unsigned int *target_freq,
 *          unsigned int old_target_freq)
 *
 * Fires in __resolve_freq() after the request was clamped to
 * policy->min/max and before the frequency-table lookup. The value written
 * here is mapped to a table entry but NOT clamped again, so honour
 * policy->max (thermal and user limits) yourself.
 *
 * android_vh_cpufreq_target is not used: for ->target_index drivers the table
 * index is computed before that hook runs, so rewriting *target_freq there does
 * not change the frequency that gets set.
 */
static void demo_resolve_freq(void *data, struct cpufreq_policy *policy,
			      unsigned int *target_freq,
			      unsigned int old_target_freq)
{
	unsigned int floor = READ_ONCE(freq_floor_khz);

	if (floor && *target_freq < floor)
		*target_freq = min(floor, policy->max);
}

/*
 * TP_PROTO(int *state, struct cpuidle_device *dev)
 *
 * Fires in cpuidle_enter_state() before the target state is taken from the
 * index. A lower index is a shallower state. A negative value makes this idle
 * entry return that value instead of idling. Runs on every idle entry.
 */
static void demo_cpu_idle_enter(void *data, int *state,
				struct cpuidle_device *dev)
{
	int cap = READ_ONCE(idle_state_cap);

	if (cap >= 0 && *state > cap)
		*state = cap;
}

static int __init demo_init(void)
{
	int ret;

	/* Takes tracepoints_mutex: process context only (module_init is fine). */
	ret = register_trace_android_vh_cpufreq_resolve_freq(demo_resolve_freq, NULL);
	if (ret) {
		pr_err("register android_vh_cpufreq_resolve_freq: %d\n", ret);
		return ret;
	}

	ret = register_trace_android_vh_cpu_idle_enter(demo_cpu_idle_enter, NULL);
	if (ret) {
		pr_err("register android_vh_cpu_idle_enter: %d\n", ret);
		goto err_resolve;
	}

	return 0;

err_resolve:
	unregister_trace_android_vh_cpufreq_resolve_freq(demo_resolve_freq, NULL);
	tracepoint_synchronize_unregister();
	return ret;
}

static void __exit demo_exit(void)
{
	/* Same (probe, data) pairs as registered, in reverse order. */
	unregister_trace_android_vh_cpu_idle_enter(demo_cpu_idle_enter, NULL);
	unregister_trace_android_vh_cpufreq_resolve_freq(demo_resolve_freq, NULL);

	/* Wait for callbacks still running on other CPUs before the code is freed. */
	tracepoint_synchronize_unregister();
}

module_init(demo_init);
module_exit(demo_exit);

/* Must be GPL-compatible: every __tracepoint_android_* is EXPORT_SYMBOL_GPL. */
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Vendor hook registration demo (plain android_vh_* hooks)");
