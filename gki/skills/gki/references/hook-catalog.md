# Vendor hook catalog

Pinned to OGKI `android15-6.6` (Linux 6.6.118, `gki_defconfig`, arm64). Hook names are listed in
`include/trace/hooks/<header>`.

- **Listed here means declared, nothing more.** Whether a hook is exported, actually called, and
  registrable on your device are separate checks (see [vendor-hooks.md](vendor-hooks.md)).
- **Kind:** `P` is `DECLARE_HOOK` (plain; can be unregistered, many probes). `R` is `DECLARE_RESTRICTED_HOOK`
  (never unregistered, 2 slots per hook).
- **Signatures** omit the leading `void *data`.
- **Out-parameters only matter if the call site reads them back.** "Default" below is the value the
  caller preloads. Leave it unchanged and the kernel takes its normal path.
- A hook with no in-tree registrant is **not** thereby free on a device. Vendor modules register
  hooks at runtime.

## By subsystem

Counts: plain / restricted as compiled, and the number of `trace_android_*()` call sites in the tree.

| Area | Header | P / R | Calls | What it covers |
|---|---|---|---|---|
| mm | `mm.h` | 177 / 19 | 228 | page allocator (`mm/page_alloc.c` 60), filemap, madvise, memory, memcontrol, shmem, readahead, compaction |
| | `vmscan.h` | 39 / 4 | 50 | reclaim: swappiness, scan balance, slab shrink, kswapd, MGLRU, folio trylock |
| | `madvise.h`, `compaction.h`, `huge_memory.h`, `swapfile.h` | 4/2, 3/0, 1/0, 1/0 | 6, 3, 1, 1 | pageout bypass, compaction, THP, swap |
| sched | `sched.h` | 31 / 85 | 123 | CPU selection, util/capacity, pick/preempt, load balance, PELT, fork/exit, affinity, prio |
| | `cgroup.h` | 4 / 5 | 9 | cgroup/cpuset attach, fork, freezer (`rvh_refrigerator`) |
| | `topology.h`, `psi.h` | 2/1, 3/0 | 4, 3 | `vh_arch_set_freq_scale`, `vh_use_amu_fie`, `rvh_cpu_capacity_show`; PSI events/triggers |
| locking | `dtask.h` | 48 / 1 | 78 | mutex/rtmutex/rwsem/percpu-rwsem wait start/finish, spinning policy, waiter ordering, lazy resched |
| | `rwsem.h`, `futex.h` | 13/0, 9/0 | 19, 9 | rwsem owner tracking/wake/steal; futex wait/wake/plist order |
| IPC | `binder.h` | 31 / 0 | 35 | binder priority, transactions, worklists, thread spawn, buffer alloc |
| net | `net.h` | 30 / 11 | 48 | socket lifecycle, TCP/UDP send/recv, TCP window/RTT/retransmit |
| power | `cpufreq.h` | 6 / 3 | 10 | frequency requests and transitions (all 9 below) |
| | `cpuidle.h`, `cpuidle_psci.h` | 2/0, 2/0 | 2, 2 | idle state choice; PSCI idle enter/exit |
| | `power.h` | 7 / 0 | 7 | freezer (`try_to_freeze_todo*`), PM QoS `freq_qos_add/update/remove_request` |
| | `thermal.h`, `suspend.h`, `psci.h`, `mpam.h` | 3/0, 2/0, 0/2, 1/0 | 4, 2, 2, 1 | thermal genl/stats, resume, PSCI suspend, MPAM |
| storage | `ufshcd.h` | 16 / 2 | 19 | UFS command send/complete, errors, crypto keys |
| | `blk.h` | 9 / 1 | 12 | `vh_check_set_ioprio` (I/O priority rewrite), blk-mq requeue/delay |
| | `fs.h`, `mmc.h`, `sd.h`, `fuse.h`, `fsnotify.h` | 6/2, 2/2, 2/0, 2/0, 1/0 | 9, 4, 2, 2, 1 | f2fs priority, umount, epoll wakeup sources, MMC/SD |
| | `dmabuf.h` | 6 / 1 | 7 | dma-buf heap alloc, release, page-pool bypass |
| security | `avc.h`, `creds.h`, `selinux.h`, `syscall_check.h`, `fips140.h` | 0/4, 0/4, 0/1, 5/0, 4/0 | 4, 4, 1, 6, 4 | SELinux AVC cache, cred commit/override, syscall checks, FIPS crypto routines |
| debug | `traps.h` 0/6, `fault.h` 1/3, `bug.h` 0/1, `debug.h` 1/0, `hung_task.h` 2/0, `softlockup.h` 1/0, `wqlockup.h` 3/3, `ftrace_dump.h` 5/0, `printk.h` 4/0, `logbuf.h` 2/1, `sysrqcrash.h` 1/0 | (left) | 1–6 each | panics, undef/BTI/FPAC traps, lockup detectors, workqueue creation, log buffers |
| irq/arch | `gic.h` 0/1, `gic_v3.h` 0/1, `preemptirq.h` 0/4, `timer.h` 1/0, `epoch.h` 2/0, `fpsimd.h` 1/0, `cpuinfo.h` 0/1, `perf.h` 0/2 | (left) | 0–6 each | IRQ affinity, irq/preempt on/off, timers, FPSIMD |
| devices | `usb.h` 4/1, `xhci.h` 2/0, `typec.h` 3/0, `iommu.h` 3/5, `regmap.h` 1/0, `remoteproc.h` 2/0, `gzvm.h` 4/0 | (left) | 1–8 each | USB/Type-C, IOMMU, remoteproc, GZVM |
| misc | `module.h` 3/0, `sys.h` 3/1, `user.h` 2/0, `signal.h` 4/0, `lz4_decompress.h` 1/0, `bpf_jit_comp.h` 0/1, `reboot.h` 0/1 | (left) | 1–4 each | module load, signals, reboot, BPF JIT |
| OGKI | `ogki_honor.h` | 24 / 13 | **0** | upstream Honor OGKI hooks: exported (except `vh_ogki_ufs_clock_scaling`), never fired by the kernel |

Useful groupings inside the big headers:

- **`sched.h` beyond the tables below:** fork/exit (`rvh_sched_fork`, `rvh_wake_up_new_task`,
  `vh_free_task`, `vh_copy_process`). Wakeup (`rvh_try_to_wake_up[_success]`, `rvh_ttwu_cond`,
  `vh_set_wake_flags`). Affinity (`rvh_sched_setaffinity`, `rvh_set_cpus_allowed_*`, `rvh_is_cpu_allowed`,
  `rvh_update_cpus_allowed`). Priority (`rvh_set_user_nice[_locked]`, `rvh_setscheduler[_prio]`,
  `vh_prio_inheritance`, `vh_prio_restore`, `vh_setscheduler_uclamp`). PELT (`rvh_attach/detach/remove_entity_load_avg`,
  `rvh_update_blocked_fair`, `vh_sched_pelt_multiplier`). Hotplug/topology (`rvh_sched_cpu_starting/dying`,
  `rvh_build_perf_domains`, `vh_build_sched_domains`). Misc (`rvh_schedule`, `rvh_set_iowait`,
  `rvh_update_misfit_status`).
- **`dtask.h`:** wait timing (`vh_{mutex,rtmutex,rwsem_read,rwsem_write}_wait_{start,finish}`,
  `vh_record_*_lock_starttime`, `rvh_percpu_rwsem_wait_complete`). Optimistic spinning
  (`vh_{mutex,rwsem}_opt_spin_{start,finish}`, `vh_{mutex,rwsem}_can_spin_on_owner`, `vh_rt_mutex_steal`).
  Waiter order and PI (`vh_alter_mutex_list_add`, `vh_task_blocks_on_rtmutex`, `vh_rtmutex_waiter_prio`,
  `vh_mutex_unlock_slowpath`). Lazy resched (`vh_set_tsk_need_resched_lazy`, `vh_resched_curr_lazy`,
  `vh_clear_curr_lazy`).
- **`vmscan.h` (43):** `vh_tune_swappiness`, `vh_use_vm_swappiness`, `vh_tune_scan_type`, `vh_tune_scan_control`,
  `vh_modify_scan_control`, `rvh_set_balance_anon_file_reclaim`, `vh_shrink_slab_bypass`, `vh_do_shrink_slab[_ex]`,
  `rvh_kswapd_shrink_node`, `rvh_vmscan_kswapd_wake/done`, `vh_direct_reclaim_begin/end`, `vh_should_continue_reclaim`,
  `vh_mglru_should_abort_scan[_order]`, `vh_evict_folios_bypass`, `vh_shrink_folio_list`, `vh_*folio_trylock*`,
  `vh_should_memcg_bypass`, `vh_mm_customize_pgdat_balanced`, `vh_mm_customize_file_is_tiny`.
- **`net.h`:** lifecycle (`rvh_inet_sock_create/release`, `vh_sk_alloc/free/clone_lock`). Data path
  (`rvh_tcp_sendmsg/recvmsg`, `rvh_udp[v6]_sendmsg/recvmsg`, `vh_udp_enqueue_schedule_skb`,
  `vh_build_skb_around`). TCP control (`rvh_tcp_select_window`, `vh_tcp_rtt_estimator`,
  `rvh_tcp_rcv_spurious_retrans`, `vh_tcp_clean_rtx_queue`, `vh_tcp_rcv_established_fast_path/slow_path`).

## Where the call sites are

There are about 815 `trace_android_*()` call sites (grep count) covering 708 distinct hooks.

| Directory | Calls | | File | Calls |
|---|---|---|---|---|
| `kernel/` | 292 | | `mm/page_alloc.c` | 60 |
| `mm/` | 263 | | `kernel/sched/core.c` | 57 |
| `drivers/` | 127 | | `mm/vmscan.c` | 51 |
| `net/` | 49 | | `kernel/sched/fair.c` | 41 |
| `fs/` | 30 | | `kernel/locking/rwsem.c` | 40 |
| `arch/` | 23 | | `drivers/android/binder.c` | 34 |
| `include/` | 11 | | `mm/filemap.c` | 29 |
| `block/` | 8 | | `drivers/ufs/core/ufshcd.c` | 18 |
| `lib/` | 7 | | `kernel/locking/mutex.c`, `mm/madvise.c` | 17 each |
| `security/` | 5 | | `kernel/workqueue.c`, `mm/compaction.c`, `mm/memory.c` | 10 each |

The allocator/reclaim paths and the scheduler are the densest. Locking, binder and UFS I/O come next.
Networking and filesystems only allow point interventions.

**39 hooks have no in-tree call site:** the 37 in `ogki_honor.h`, plus `android_rvh_gic_v3_set_affinity`
(`gic_v3.h`) and `android_rvh_try_alloc_pages` (`mm.h`). The exported ones can be registered, but the kernel never
fires them. `android_vh_ogki_ufs_clock_scaling` is not even exported.

## Performance and scheduling hooks

Signatures were checked against the 6.6.118 headers and call sites. Almost all scheduler hooks are `R`.
Many take private types (`struct rq`, `cfs_rq`, `rq_flags`, `sched_group`), see "The type trap" in
[vendor-hooks.md](vendor-hooks.md).

### Placement and CPU selection (`sched.h`)

| Hook | K | Signature | Out-param effect |
|---|---|---|---|
| `android_rvh_select_task_rq_fair` | R | `(struct task_struct *p, int prev_cpu, int sd_flag, int wake_flags, int *new_cpu)` | default `-1`; `>= 0` is returned as the CFS target CPU |
| `android_rvh_find_energy_efficient_cpu` | R | `(struct task_struct *p, int prev_cpu, int sync, int *new_cpu)` | default `INT_MAX`; any other value is returned (EAS path) |
| `android_rvh_select_task_rq_rt` | R | same as `select_task_rq_fair` | default `-1`; `>= 0` returned |
| `android_rvh_find_lowest_rq` | R | `(struct task_struct *p, struct cpumask *local_cpu_mask, int ret, int *lowest_cpu)` | default `-1`; `>= 0` returned |
| `android_rvh_select_fallback_rq` | R | `(int cpu, struct task_struct *p, int *new_cpu)` | default `-1`; `>= 0` returned |

**Calling context of `android_rvh_select_task_rq_fair`** (read from the 6.6.118 call sites):

- It is the first statement of `select_task_rq_fair()` (`kernel/sched/fair.c`), before that function's
  own `rcu_read_lock()`. When the hook has a probe and this is not a fork, `sync_entity_load_avg(&p->se)`
  runs just before it, so `p->se.avg` is current.
- All three callers hold `p->pi_lock`, a raw spinlock taken with `irqsave`: IRQs and preemption are off.
  No rq lock is held.

| Path | Caller (`kernel/sched/core.c`) | `sd_flag` |
|---|---|---|
| wakeup | `try_to_wake_up()` → `select_task_rq()` | `SD_BALANCE_WAKE` |
| fork | `wake_up_new_task()` → `select_task_rq()` | `SD_BALANCE_FORK` |
| exec | `sched_exec()` → `p->sched_class->select_task_rq()` | `SD_BALANCE_EXEC` |

- Forbidden: sleeping, `GFP_KERNEL`, mutexes, rwsems, semaphores. Use `printk_deferred()`, not `printk()`,
  as `select_fallback_rq()` does under the same lock. Take `rcu_read_lock()` yourself before reading
  RCU-protected data such as sched domains.
- `sd_flag` is `wake_flags & 0xF`. Test it against the public `SD_BALANCE_*` enum
  (`include/linux/sched/topology.h`). The `WF_*` names are private to `kernel/sched/sched.h`, which
  `static_assert`s that the two match.
- The returned CPU is still checked. Wakeup and fork pass it through `select_task_rq()`, which replaces a
  CPU that `is_cpu_allowed()` rejects with `select_fallback_rq()`. Exec ignores an inactive CPU, and
  `__migrate_task()` drops a disallowed one. Choose from `p->cpus_ptr` and `cpu_active_mask` anyway.

**Other restricted scheduler hooks.** Many fire with the rq lock held (raw spinlock, IRQs off):
`android_rvh_enqueue_task` / `_dequeue_task` and their `after_` twins (`enqueue_task()` /
`dequeue_task()` in `kernel/sched/core.c`), and `android_rvh_tick_entry` (inside `rq_lock()` in
`scheduler_tick()`, from the tick interrupt). The same rules apply. Also do not wake a task or take
another rq lock from them (inferred from rq-lock ordering). Read the call site of any hook not named here.

### Capacity and utilization (`sched.h`)

| Hook | K | Signature | Out-param effect |
|---|---|---|---|
| `android_rvh_util_fits_cpu` | R | `(unsigned long util, unsigned long uclamp_min, unsigned long uclamp_max, int cpu, bool *fits, bool *done)` | set `*done = true` and `*fits` to decide |
| `android_rvh_task_fits_cpu` | R | `(struct task_struct *tsk, unsigned long util, unsigned long uclamp_min, unsigned long uclamp_max, int cpu, bool *fits, bool *done)` | same |
| `android_rvh_update_cpu_capacity` | R | `(int cpu, unsigned long *capacity)` | value stored directly as the rq/group capacity |
| `android_rvh_effective_cpu_util` | R | `(int cpu, unsigned long util_cfs, unsigned long max, int type, struct task_struct *p, unsigned long *new_util)` | default `ULONG_MAX`; other values returned. Feeds schedutil. |
| `android_rvh_cpu_util_cfs_boost` | R | `(int cpu, unsigned long *util)` | default `INT_MAX`; other values returned |
| `android_rvh_cpu_overutilized` | R | `(int cpu, int *overutilized)` | default `-1`; `0`/`1` returned |
| `android_rvh_uclamp_eff_get` | R | `(struct task_struct *p, enum uclamp_id clamp_id, struct uclamp_se *uclamp_max, struct uclamp_se *uclamp_eff, int *ret)` | set `*ret` non-zero and fill `*uclamp_eff`: per-task effective uclamp |
| `android_rvh_util_est_update` | R | `(struct cfs_rq *cfs_rq, struct task_struct *p, bool task_sleep, int *ret)` | `*ret` non-zero skips the util_est update |
| `android_rvh_update_load_avg` | R | `(u64 now, struct cfs_rq *cfs_rq, struct sched_entity *se)` | notification |
| `android_vh_map_util_freq` | P | `(unsigned long util, unsigned long freq, unsigned long cap, unsigned long *next_freq, struct cpufreq_policy *policy, bool *need_freq_update)` | default `0`; non-zero replaces schedutil's util→freq mapping (`kernel/sched/cpufreq_schedutil.c`) |

### Pick, preemption and tick (`sched.h`)

| Hook | K | Signature | Notes |
|---|---|---|---|
| `android_rvh_before_pick_task_fair` | R | `(struct rq *rq, struct task_struct **p, struct sched_entity **se, struct task_struct *prev, struct rq_flags *rf)` | a non-NULL `*p` jumps past the normal pick, on the group-scheduling path only. Read the call site. |
| `android_rvh_replace_next_task_fair` | R | `(struct rq *rq, struct task_struct **p, struct sched_entity **se, bool *repick, bool simple, struct task_struct *prev)` | two call sites with different semantics (`simple`); read `pick_next_task_fair()` first |
| `android_rvh_check_preempt_wakeup` | R | `(struct rq *rq, struct task_struct *p, bool *preempt, bool *nopreempt, int wake_flags, struct sched_entity *se, struct sched_entity *pse, int next_buddy_marked)` | force or suppress wakeup preemption |
| `android_rvh_check_preempt_wakeup_ignore` | R | `(struct task_struct *p, bool *ignore)` | `*ignore = true` skips the wakeup-preemption check |
| `android_rvh_update_deadline` | R | `(struct cfs_rq *cfs_rq, struct sched_entity *se, bool *skip_preempt)` | `*skip_preempt = true` returns early: no new deadline, no resched |
| `android_rvh_place_entity` | R | `(struct cfs_rq *cfs_rq, struct sched_entity *se, int initial, u64 *vruntime)` | **observe only.** In 6.6.118 this is the last statement of `place_entity()` (`kernel/sched/fair.c:5320`), after `se->vruntime` and `se->deadline` are set. The local `vruntime` is never read back, so writing `*vruntime` changes nothing. Do not use it to steer placement or vruntime. |
| `android_rvh_tick_entry` / `android_vh_scheduler_tick` | R / P | `(struct rq *rq)` | per-tick notification |
| `android_rvh_context_switch` | R | `(struct task_struct *pre, struct task_struct *next)` | notification |
| `android_rvh_enqueue_task` / `_dequeue_task` / `_after_enqueue_task` / `_after_dequeue_task` | R | `(struct rq *rq, struct task_struct *p, int flags)` | notifications around core enqueue/dequeue |

### Task lifecycle (`sched.h`)

| Hook | K | Signature | Call site / notes |
|---|---|---|---|
| `android_vh_dup_task_struct` | P | `(struct task_struct *tsk, struct task_struct *orig)` | end of `dup_task_struct()` (`kernel/fork.c`), after the child `tsk` was copied from `orig`. No pid yet. |
| `android_vh_free_task` | P | `(struct task_struct *p)` | `free_task()` (`kernel/fork.c`), just before the `task_struct` is freed; also on `copy_process()` failure. Can run from an RCU callback. |
| `android_vh_copy_process` | P | `(struct task_struct *p, int nr_threads)` | late in `copy_process()` under `tasklist_lock`; `p` is **`current`** (the parent), not the child |
| `android_rvh_sched_fork` | R | `(struct task_struct *p)` | start of `sched_fork()` (`kernel/sched/core.c`); `p` is the child |

### Load balance (`sched.h`)

| Hook | K | Signature | Out-param effect |
|---|---|---|---|
| `android_rvh_can_migrate_task` | R | `(struct task_struct *p, int dst_cpu, int *can_migrate)` | `0` pins the task against load-balance migration |
| `android_rvh_sched_newidle_balance` | R | `(struct rq *this_rq, struct rq_flags *rf, int *pulled_task, int *done)` | `*done` non-zero returns `*pulled_task` and skips newidle balance |
| `android_rvh_find_busiest_group` | R | `(struct sched_group *busiest, struct rq *dst_rq, int *out_balance)` | EAS-only call site |
| `android_rvh_find_busiest_queue` | R | `(int dst_cpu, struct sched_group *group, struct cpumask *env_cpus, struct rq **busiest, int *done)` | `*done` returns `*busiest` |
| `android_rvh_sched_nohz_balancer_kick` | R | `(struct rq *rq, unsigned int *flags, int *done)` | `*done` jumps to the kick with your `*flags` |
| `android_rvh_find_new_ilb` | R | `(struct cpumask *nohz_idle_cpus_mask, int *ilb)` | default `-1`; `>= 0` picks the idle-load-balance CPU |
| `android_rvh_migrate_queued_task` | R | `(struct rq *rq, struct rq_flags *rf, struct task_struct *p, int new_cpu, int *detached)` | `*detached` means you did the migration |
| `android_rvh_sched_rebalance_domains` | R | `(struct rq *rq, int *continue_balancing)` | `0` skips this rebalance pass |

### `cpufreq.h`: all 9

| Hook | K | Signature | Call site / notes |
|---|---|---|---|
| `android_rvh_show_max_freq` | R | `(struct cpufreq_policy *policy, unsigned int *max_freq)` | sysfs `cpuinfo_max_freq` show |
| `android_vh_freq_table_limits` | P | `(struct cpufreq_policy *policy, unsigned int min_freq, unsigned int max_freq)` | `drivers/cpufreq/freq_table.c` |
| `android_vh_cpufreq_acct_update_power` | P | `(u64 cputime, struct task_struct *p, unsigned int state)` | `drivers/cpufreq/cpufreq_times.c` |
| `android_vh_cpufreq_resolve_freq` | P | `(struct cpufreq_policy *policy, unsigned int *target_freq, unsigned int old_target_freq)` | in `__resolve_freq()`, **after** the clamp to `policy->min/max` and before the table lookup. The written value is mapped to a table entry but **not re-clamped**, so respect `policy->max` yourself. Used by schedutil and by `__cpufreq_driver_target()`. |
| `android_vh_cpufreq_fast_switch` | P | same | after the clamp, passed straight to `->fast_switch()` (not re-clamped) |
| `android_vh_cpufreq_target` | P | same | after `__resolve_freq()`. For `->target_index` drivers the index was already cached before this hook, so rewriting `*target_freq` only affects the `== policy->cur` shortcut. Only `->target` drivers receive the new value. |
| `android_rvh_cpufreq_transition` | R | `(struct cpufreq_policy *policy)` | after a frequency change (normal and fast-switch paths) |
| `android_vh_cpufreq_online` | P | `(struct cpufreq_policy *policy)` | policy online |
| `android_rvh_cpufreq_create_policy` | R | `(struct cpufreq_policy *policy)` | policy creation |

### `cpuidle.h`: 2 plain hooks

| Hook | Signature | Notes |
|---|---|---|
| `android_vh_cpu_idle_enter` | `(int *state, struct cpuidle_device *dev)` | In `cpuidle_enter_state()`, before the target state is chosen from the index. Lower the index for shallower idle. A negative value returns it and abandons this idle entry. Runs on every idle entry: keep it tiny. |
| `android_vh_cpu_idle_exit` | `(int state, struct cpuidle_device *dev)` | notification |

`cpuidle_psci.h` adds `android_vh_cpuidle_psci_enter/exit` (plain).

### Memory and reclaim (`mm.h`, `vmscan.h`, `madvise.h`)

| Hook | K | Signature | Purpose |
|---|---|---|---|
| `android_vh_tune_swappiness` | P | `(int *swappiness)` | per-call swappiness |
| `android_vh_tune_scan_type` | P | `(enum scan_balance *scan_type)` | anon/file scan balance. `enum scan_balance` is private to `mm/vmscan.c`: do not copy its values. |
| `android_rvh_set_balance_anon_file_reclaim` | R | `(bool *balance_anon_file_reclaim)` | anon/file balance |
| `android_vh_modify_scan_control` | P | `(u64 *ext, unsigned long *nr_to_reclaim, struct mem_cgroup *target_mem_cgroup, bool *file_is_tiny, bool *may_writepage)` | several reclaim knobs at once |
| `android_vh_direct_reclaim_begin` / `_end` | P | `(int *prio)` / `(int prio)` | direct-reclaim bracket |
| `android_rvh_kswapd_shrink_node` | R | `(unsigned long *nr_reclaimed)` | kswapd per-node |
| `android_vh_do_shrink_slab_ex` | P | `(struct shrink_control *shrinkctl, struct shrinker *shrinker, long *freeable, int priority)` | per-shrinker freeable |
| `android_vh_shrink_slab_bypass` | P | `(gfp_t gfp_mask, int nid, struct mem_cgroup *memcg, int priority, bool *bypass)` | skip slab shrink |
| `android_vh_get_page_wmark` | P | `(unsigned int alloc_flags, unsigned long *page_wmark)` | watermark used by the allocator |
| `android_rvh_alloc_pages_adjust_wmark` | R | `(gfp_t gfp_mask, int order, int *alloc_flags)` | slow-path watermark flags. The `vh_` twin is marked deprecated in `mm/page_alloc.c` but still called. |
| `android_rvh_alloc_pages_reset_wmark` | R | `(gfp_t gfp_mask, int order, int *alloc_flags, unsigned long *did_some_progress, int *no_progress_loops, unsigned long direct_reclaim_retries)` | same. The `vh_` twin is deprecated. |
| `android_vh_should_alloc_pages_retry` | P | `(gfp_t gfp_mask, int order, int *alloc_flags, int migratetype, struct zone *preferred_zone, struct page **page, bool *should_alloc_retry)` | retry decision |
| `android_rvh_perform_reclaim` | R | `(int order, gfp_t gfp_mask, nodemask_t *nodemask, unsigned long *progress, bool *skip)` | replace or skip direct reclaim |
| `android_vh_customize_thp_pcp_order` | P | `(unsigned int *order)` | THP per-cpu-pages order |
| `android_vh_madvise_pageout_bypass` | P | `(struct mm_struct *mm, bool pageout, int *ret)` | `MADV_PAGEOUT`/`COLD` bypass |

### `binder.h`: all plain

All `binder.h` hooks are `DECLARE_HOOK`, so a binder-tuning module can be unloaded. But `binder_proc`,
`binder_thread`, `binder_transaction` and `binder_work` are private (`drivers/android/binder_internal.h`).
Only the `task_struct` arguments can be used without their layouts.

| Hook | Signature | Purpose |
|---|---|---|
| `android_vh_binder_set_priority` / `_restore_priority` | `(struct binder_transaction *t, struct task_struct *task)` | priority hand-off to/from the server thread |
| `android_vh_sync_txn_recvd` | `(struct task_struct *tsk, struct task_struct *from)` | sync transaction received (caller → callee pairing) |
| `android_vh_binder_proc_transaction` | `(struct task_struct *caller_task, struct task_struct *binder_proc_task, struct task_struct *binder_th_task, int node_debug_id, struct binder_transaction *t, bool pending_async)` | transaction queued |
| `android_vh_binder_proc_transaction_finish` | `(struct binder_proc *proc, struct binder_transaction *t, struct task_struct *binder_th_task, bool pending_async, bool sync)` | queued, after wakeup |
| `android_vh_binder_wait_for_work` | `(bool do_proc_work, struct binder_thread *tsk, struct binder_proc *proc)` | thread about to wait |
| `android_vh_binder_select_special_worklist` | `(struct list_head **list, struct binder_thread *thread, struct binder_proc *proc, int wait_for_proc_work, bool *nothing_to_do)` | choose an alternate work list |
| `android_vh_binder_special_task` | `(struct binder_transaction *t, struct binder_proc *proc, struct binder_thread *thread, struct binder_work *w, struct list_head *head, bool sync, bool *special_task)` | route work to that list |
| `android_vh_binder_spawn_new_thread` | `(struct binder_thread *thread, struct binder_proc *proc, bool *force_spawn)` | force a looper spawn |
| `android_vh_binder_alloc_new_buf_locked` | `(size_t size, size_t *free_async_space, int is_async, bool *should_fail)` | async buffer policy |
| `android_vh_binder_ioctl_end` | `(struct task_struct *caller_task, unsigned int cmd, unsigned long arg, struct binder_thread *thread, struct binder_proc *proc, int *ret)` | ioctl exit |
