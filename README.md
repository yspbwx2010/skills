# Skills

简体中文 | [English](README.en.md)

自用的一些 [Agent Skills](https://agentskills.io/specification), 只保证满足我自己的需求, 不做更多承诺

每个 skill 都可以单独安装, 按需取用即可

## Skill 列表

| Skill | 用途 |
| --- | --- |
| [miuix](miuix/README.md) | 用 [Miuix](https://github.com/compose-miuix-ui/miuix) 写应用 |
| [kpm](kpm/README.md) | 编写 [KernelPatch](https://github.com/bmax121/KernelPatch) 模块 (KPM) |
| [apm](apm/README.md) | 编写 Magisk 模块 (APM) |
| [metamodule](metamodule/README.md) | 编写 [metamodule](https://kernelsu.org/zh_CN/guide/metamodule.html) (元模块) |

## 安装

> 把 `<skill>` 换成上表中的名字

### 1. Skills CLI (Claude Code, Codex, Cursor, OpenCode 等 40+ 种 agent)

```bash
npx skills add yspbwx2010/skills --skill <skill>
npx skills add yspbwx2010/skills --list      # 查看仓库里的全部 skill
```

### 2. Claude Code 插件市场

```text
/plugin marketplace add yspbwx2010/skills
/plugin install <skill>@yspbwx2010-skills
```

### 3. 手动复制

把 `<skill>/skills/<skill>/` 复制到 agent 的 skills 目录, 比如 Claude Code 的 `~/.claude/skills/`

其他 agent 的目录见各 skill 的 README

## 目录结构

每个 skill 一个目录, README, 更新日志, 维护说明和工具都放在各自目录里, 安装时只复制 `<skill>/skills/<skill>/`

详细结构和新增 skill 的步骤见 [AGENTS.md](AGENTS.md)

## 许可证

[MIT](LICENSE)
