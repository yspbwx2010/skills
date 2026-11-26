# apm

简体中文 | [English](README.en.md)

让你的 Coding Agent 会给 [APatch](https://github.com/bmax121/APatch) 和 [KernelSU](https://github.com/tiann/KernelSU) 写 **Magisk 式 systemless 模块**: `module.prop`, zip + `customize.sh` 安装流程, 改 `/system`, 启动脚本, `sepolicy.rule`, WebUI

对齐 **APatch 管理器 11224** 和 **KernelSU v3.3.1**. 两家现在都把挂载交给元模块 (metamodule): 没装挂载用的元模块, 模块的 `system/` 就不会挂上. 规则取自 APatch 的 `apd`, KernelSU 的 `ksud` 和各自的安装脚本, 不是只看文档 (文档已滞后, 比如 `MAGISK_VER_CODE` 安装脚本里是 30000, 文档还写 27000)

## 它做什么

- **模块结构**: 安装后的 `/data/adb/modules/<id>/` 目录树, 标记文件 (`skip_mount` / `disable` / `remove`), 以及 `apd` 强制校验 id 正则的 `module.prop`
- **systemless**: 挂载由元模块负责 (`meta-overlayfs` 用 overlayfs, magic mount 类元模块用 bind mount); 如何新增, 删除 (whiteout / `REMOVE`), 替换 (`REPLACE` / opaque 属性, KernelSU v3 要元模块定义 `mark_replace`) 系统路径
- **脚本**: 各启动阶段, 哪个会阻塞启动 (KernelSU 每阶段最多 35 秒, APatch 不设超时), 两家真实的执行顺序 (`post-fs-data` 和挂载的先后相反), 每个阶段的环境变量 (`APATCH=true` / `KSU=true` 等), 通用 `.d` 脚本, Lua 阶段脚本
- **安装**: zip 格式, `customize.sh` 的变量和函数, `SKIPUNZIP`, 精确的安装顺序
- **附加功能**: WebUI (`webroot/`), Action 按钮, metamodule (含带自定义安装器的 metamodule 会拦住普通模块安装的情况)
- **移植**: 从 Magisk 移植过来的差异 (没有 Zygisk, `/data/adb/ap/` 和 `/data/adb/ksu/` 路径, 挂载看元模块, APatch 只支持 arm64, `APATCH` / `KSU` 环境变量)
- **脚手架**: `scripts/new_module.py` 生成合法的模块骨架 (可选顺带打出可刷入的 zip)

## 安装

```bash
npx skills add yspbwx2010/skills --skill apm
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install apm@yspbwx2010-skills
```

或者把 `apm/skills/apm/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

[MIT](../LICENSE)
