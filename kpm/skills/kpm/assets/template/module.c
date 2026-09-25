/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <compiler.h>
#include <kpmodule.h>
#include <linux/printk.h>
#include <linux/string.h>
#include <kputils.h>

KPM_NAME("__NAME__");
KPM_VERSION("1.0.0");
KPM_LICENSE("GPL v2");
KPM_AUTHOR("__AUTHOR__");
KPM_DESCRIPTION("__DESCRIPTION__");

static long mod_init(const char *args, const char *event, void *__user reserved)
{
    pr_info("[__NAME__] init, event: %s, args: %s\n", event, args ? args : "");
    pr_info("[__NAME__] kernelpatch version: %x, kernel version: %x\n", kpver, kver);
    /* Install hooks here. Remember to undo every one of them in mod_exit. */
    return 0;
}

static long mod_ctl0(const char *ctl_args, char *__user out_msg, int outlen)
{
    /* Reply to userspace `sc_kpm_control`. out_msg is a USER buffer. */
    char buf[64] = "echo: ";
    strncat(buf, ctl_args, sizeof(buf) - strlen(buf) - 1);
    compat_copy_to_user(out_msg, buf, strlen(buf) + 1);
    return 0;
}

static long mod_exit(void *__user reserved)
{
    /* Undo everything mod_init installed. A hook left here panics the kernel on unload. */
    pr_info("[__NAME__] exit\n");
    return 0;
}

KPM_INIT(mod_init);
KPM_CTL0(mod_ctl0);
KPM_EXIT(mod_exit);
