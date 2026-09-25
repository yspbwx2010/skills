# xlings

简体中文 | [English](README.en.md)

让你的 Coding Agent 会用 **[xlings](https://github.com/openxlings/xlings)** 包管理器: 装包删包, 多版本 `use` 切换, SubOS 创建与沙箱, 项目模式 `.xlings.json`, 自定义索引仓, 镜像与国内网络, 给 CI / agent 用的机读输出, 以及它和 mcpp 的集成

对齐 **xlings 2026.9.20.1**. 命令写法对过 2026.9.14.1 的 `--help`, 之后两个版本的变化读自源码和已合并的 PR

## 它做什么

- **命令**: 16 个顶层命令和 5 个命令组的全部参数, 别名, 退出码
- **配置与目录**: 全局 / 项目 `.xlings.json` 逐字段, home 布局, 包落地位置, 环境变量和 `XLINGS_HOME` 解析链
- **SubOS**: 创建, 使用, 沙箱, 环境不串 home 的隔离做法
- **机读输出**: 四层输出, 20 项 capability, NDJSON 事件, 接 CI
- **排障**: 按症状索引 (自更新卡死, 设了镜像不生效, SubOS 不报自身信息 ...)
- **打包**: 写 xim-pkgindex 包的完整流程 (`spec = "2"`, hooks, `xvm.add`, 镜像), 以及一个包该进 xim-pkgindex 还是 mcpp-index
- **和 mcpp 的集成**: `MCPP_VENDORED_XLINGS`, `[xlings] deps`, 两个 home 互不读写
- **上游文档偏差**: 上游文档和实现对不上的地方

## 安装

```bash
npx skills add yspbwx2010/skills --skill xlings
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install xlings@yspbwx2010-skills
```

或者把 `xlings/skills/xlings/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

[MIT](../LICENSE)
