# kpm

简体中文 | [English](README.en.md)

让你的 Coding Agent 会写, 会编译, 会加载 **KernelPatch 模块 (KPM)**: 一种 arm64 ELF 对象, 由 [KernelPatch](https://github.com/bmax121/KernelPatch) 和 [APatch](https://github.com/bmax121/APatch) 加载进 Linux 内核里运行, 用来 inline hook 内核函数, hook 系统调用, 或在没有内核源码时按名字调用内核函数

对齐 **KernelPatch 0.13.9**. 每个宏, API 签名, 导出符号名和加载器规则都是从 KernelPatch 源码和 APatch 守护进程读出来的, 不是抄官方文档 (文档已和源码脱节)

## 它做什么

- **结构与生命周期**: 元数据宏, 五个回调 (`KPM_INIT` / `KPM_CTL0` / `KPM_CTL1` / `KPM_EXIT` / `KPM_EVENT`) 的精确签名, 以及那条不遵守就崩内核的规则: 所有 hook 必须在 `exit` 里撤销
- **真实的导出 API**: 约 113 个 `KP_EXPORT_SYMBOL` 符号按头文件分组带签名, 外加文档与源码不符的坑 (比如 `commit_su` / `task_su` 其实没有导出)
- **Hook**: inline `hook_wrap` 链, 函数指针 hook, `hook_err_t` 错误码, 链的执行顺序和 16 项上限; 系统调用 hook 家族, `syscall_argn` 取参, 覆盖返回值
- **编译**: `aarch64-none-elf` 工具链, `-r` 部分链接的 Makefile, `-fno-common`, `.lds`, 以及加载器对 ELF 的检查
- **加载**: SuperCall 的 `sc_kpm_load` / `control` / `unload`, `kptools` 的内嵌参数和启动事件, APatch 的 `/data/adb/ap/kpm/` 自动加载路径
- **脚手架**: `scripts/new_kpm.py` 在空目录里生成能直接编译的 KPM 骨架

## 安装

```bash
npx skills add yspbwx2010/skills --skill kpm
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install kpm@yspbwx2010-skills
```

或者把 `kpm/skills/kpm/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 它生成的代码需要什么

- `aarch64-none-elf` GCC 工具链 (或 `clang --target=aarch64-none-elf`) 来编译 `.kpm`
- 一份对应版本的 KernelPatch 源码, 用来提供头文件
- 一台被 KernelPatch / APatch 打过补丁的 arm64 设备 (Linux 3.18-6.6, `CONFIG_KALLSYMS=y`)

## 许可证

[MIT](../LICENSE)
