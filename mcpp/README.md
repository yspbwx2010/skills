# mcpp

简体中文 | [English](README.en.md)

让你的 Coding Agent 会用 **[mcpp](https://github.com/mcpp-community/mcpp)**: C++23 模块化构建工具. 构建, 测试, 门禁, `mcpp.toml`, workspace, 工具链与交叉编译, 缓存, CI 机读输出, 给 mcpp 本身提 issue / PR, 以及把库打包进 [mcpp-index](https://github.com/mcpplibs/mcpp-index)

对齐 **mcpp 2026.9.24.1**. 结论都标了出处 (源码 `文件:行号`, 文档, issue 号), 文档和源码不一致时以源码为准

## 它做什么

- **先读的纠错**: `build` / `test` / `run` 默认 dev 配置, `mcpp.lock` 要 `--locked` 才生效, 快路径重放造成的假绿, 只看 mtime 判陈旧导致 `tar` / `cp -p` 回滚假绿, `MCPP_HOME` 由二进制位置推出且不能搬
- **日常命令与门禁**: 命令语义和坑, 机读输出 (envelope, NDJSON 事件, `reason` 全集), 测试系统, 大 workspace 的门禁开销
- **配置**: `mcpp.toml` 逐节逐字段, workspace 继承, `cfg()` 谓词, 依赖选择器, `[hooks]` 与 `build.mcpp` / `mcpp::action`
- **交叉与异构**: target 选择, 工具链, wasm / Android / iOS, 裸机 freestanding, 加速器与构建插件
- **缓存**: 各层缓存按什么做 key, 怎么安全地清
- **排障**: 按症状索引的故障手册
- **版本史**: 2026.9.1.1 到 2026.9.24.1 每个版本用户可见的变化和新写法
- **给上游贡献**: issue 与提交信息写法, 自举构建, CI, 发版流程, 对外沟通规则
- **打包**: mcpp-index 描述文件字段, features, GLOBAL + CN 镜像, lint, 隔离 home 的本地验证

## 安装

```bash
npx skills add yspbwx2010/skills --skill mcpp
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install mcpp@yspbwx2010-skills
```

或者把 `mcpp/skills/mcpp/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

[MIT](../LICENSE)
