# gki

简体中文 | [English](README.en.md)

让你的 Coding Agent 会给 **Android GKI** (通用内核镜像) 写树外内核模块, 并且改内核时不破坏 **KMI** (内核模块接口): 设备上原厂的 vendor 模块只认 KMI, 符号, CRC 或结构布局对不上就加载失败, 对上了也不代表语义兼容

对齐 **OGKI android15-6.6** (一加面向 ACK `android15-6.6` 的通用内核树), Linux 6.6.118, KMI 第 8 代, `gki_defconfig`, arm64. 每个数字, 配置值和 hook 签名都是从内核源码和一次真实的 `gki_defconfig` 构建里读出来的, 依赖配置的结论都附了在你自己的树上复查的命令

## 它做什么

- **反直觉的事实先说**: 本地构建里 `CONFIG_MODULE_SIG_PROTECT=y` 但受保护符号闸门是空的, `CONFIG_FUNCTION_TRACER` 关闭 (没有 ftrace, fprobe, livepatch) 而 kprobe 可用, `CONFIG_TRIM_UNUSED_KSYMS` 关闭, `M=` 编出来的模块不签名
- **KMI 由什么组成**: `abi_gki_aarch64*` 符号列表, `.stg` 里的类型布局 (包括 `struct rq` 这类 "私有" 类型), 改变布局的 Kconfig, 以及 CRC 查不出来的东西 (inline 函数体, `HZ` 这类常量, `__GENKSYMS__`, `CONFIG_SLIM_SCHED`)
- **KCFI**: 回调原型必须逐字一致, 不许强转函数指针, `__nocfi` 救不了不匹配的回调, 影子调用栈和 x18
- **Vendor hook**: 声明, 导出, 真被调用, 运行时能注册是四件事; 普通 hook 与 restricted hook 的区别 (后者不能注销, 每个 hook 只有 2 个槽位, 模块永远卸不掉); 按子系统整理的 hook 目录和常用签名
- **选路径**: 树外模块, vendor hook, kprobe, 改 defconfig, 改源码, 按顺序选第一个能用的
- **自编内核必须保留什么**: 必须保持的配置和布局, 可以放宽的部分, vendor/OEM 数据槽为什么不是空闲的, 改动前的检查清单
- **模板**: `assets/` 下两个能直接编译的模块 (kprobe + reboot notifier, 两个普通 vendor hook), 对 6.6.118 构建编译零警告

## 安装

```bash
npx skills add yspbwx2010/skills --skill gki
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install gki@yspbwx2010-skills
```

或者把 `gki/skills/gki/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 它生成的代码需要什么

- 内核源码树, 以及对它做过一次完整构建的输出目录 (`.config` 和完整的 `Module.symvers`, 只 `make Image` 不够)
- 该 ACK 分支固定的 clang (android15-6.6 是 clang-r510928 / LLVM 18.0.0)
- 一台运行这份源码编出来的内核的 arm64 设备; 原厂内核通常会裁剪符号并启用符号闸门, 本地构建的那些 "自由" 在原厂内核上不成立

## 许可证

[MIT](../LICENSE)
