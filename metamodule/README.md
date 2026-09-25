# metamodule

简体中文 | [English](README.en.md)

让你的 Coding Agent 会写 **metamodule (元模块)**: [KernelSU](https://github.com/tiann/KernelSU) (以及沿用该设计的 [APatch](https://github.com/bmax121/APatch)) 里可插拔的模块挂载 / 安装后端. metamodule (`module.prop` 里带 `metamodule=1`) 通过 `metamount.sh` / `metainstall.sh` / `metauninstall.sh` 决定普通模块怎么挂到 `/system`, 怎么安装. 没有它, KernelSU 什么都不挂

对照 KernelSU 的 `ksud` 源码和官方 [metamodule 文档](https://kernelsu.org/zh_CN/guide/metamodule.html)核对, 并与 APatch 的 `apd` 交叉验证

## 它做什么

- **契约**: `metamodule=1`, id 用 `meta-` 前缀的约定, 单实例规则, `/data/adb/metamodule` 软链接
- **三个 hook**: `metamount.sh` (挂载后端; 环境变量 `MODULE_DIR`; 每个挂载都必须把 source 设成 `"KSU"`), `metainstall.sh` (普通模块安装时被 source, 可用 `install_module`), `metauninstall.sh` (清理; 模块 id 是环境变量 `MODULE_ID`, 不是 `$1`, 一个文档与源码不符的坑)
- **启动顺序**: `metamount.sh` 到底何时跑 (在所有 post-fs-data 之后), 以及它是阻塞的
- **安装被拦**: 普通模块安装为什么会被拒 (带 `metainstall.sh` 的 metamodule 处于不稳定状态时), 怎么解除
- **参考实现**: `meta-overlayfs` 怎么做 (双目录 + ext4 镜像), 外加一个最小的 bind-mount metamodule
- **KernelSU 与 APatch 差异**: 环境变量名和 busybox 路径的不同
- **脚手架**: `scripts/new_metamodule.py` 生成合法的 metamodule (可选顺带打 zip)

## 安装

```bash
npx skills add yspbwx2010/skills --skill metamodule
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install metamodule@yspbwx2010-skills
```

或者把 `metamodule/skills/metamodule/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

[MIT](../LICENSE)
