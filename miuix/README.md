# miuix

简体中文 | [English](README.en.md)

![License](https://img.shields.io/badge/license-MIT-blue)
![Miuix](https://img.shields.io/badge/Miuix-0.9.4-3482FF)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-8A2BE2)

让你的 Coding Agent 会用 [Miuix](https://github.com/compose-miuix-ui/miuix), 复刻小米 HyperOS 视觉的 Compose Multiplatform UI 库

从空目录一条命令生成能直接编译的 Android / 桌面 / Web 工程, 之后写的界面代码第一次编译就过: 每个签名都从 Miuix 源码抽出, 每条陷阱都带 `文件:行号` 证据

## 它做什么

- **从空目录起工程**: `scripts/new_app.py` 生成 Kotlin Multiplatform (Android / 桌面 / Web, 可任选) 或纯 Android 工程, 自带 Gradle wrapper, 示例 `App.kt` 已示范主题 / 可折叠标题栏 / 设置项分组 / 页面导航 / 确认对话框
- **签名是抽出来的, 不是抄的**: 183 个 `@Composable`, 54 个顶层函数, 37 个 `Defaults`, 177 个公开类型, 943 个图标, 全部由脚本从源码生成, 每处都链到 GitHub 上 `v0.9.4` 的对应行
- **带证据的陷阱**: 174 个条目 / 696 条陷阱 (200 条会导致编译失败, 崩溃或明显错误), 每条都引用证明它的源码行
- **按主题拆分的参考**: 17 个生成的主题文件加手写配方, agent 按需读取, 不会一次塞满上下文

## 安装

```bash
npx skills add yspbwx2010/skills --skill miuix
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install miuix@yspbwx2010-skills
```

或者把 `miuix/skills/miuix/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 版本

对齐 Miuix **0.9.4** (Maven Central 正式版) · Kotlin 2.4.20 / Compose Multiplatform 1.12.0 · compileSdk 37 / minSdk 24 · JDK 21

只对齐正式发布版, 不对齐 main 分支: main 上的破坏性改动写进参考会让代码在正式版上编译失败

## 维护

维护与升级流程见 [CONTRIBUTING.md](CONTRIBUTING.md) (英文)

## 许可证

[MIT](../LICENSE)
