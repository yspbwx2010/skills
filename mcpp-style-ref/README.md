# mcpp-style-ref

简体中文 | [English](README.en.md)

让你的 Coding Agent 按 **Modern / Module C++ (C++23)** 风格写代码: 标识符命名, 模块与 `.cppm` / `.cpp` 组织, `import std`, 常用惯用法 (`auto`, 花括号初始化, 智能指针, `string_view`, `optional` / `expected`, RAII)

内容取自 mcpp 社区的 [mcpp-style-ref](https://github.com/mcpp-community/mcpp-style-ref) (提交 `c9ddaf7`), 只把两处指向原仓库的相对链接改成了绝对链接, 并在 frontmatter 里加了许可证

## 安装

```bash
npx skills add yspbwx2010/skills --skill mcpp-style-ref
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install mcpp-style-ref@yspbwx2010-skills
```

或者把 `mcpp-style-ref/skills/mcpp-style-ref/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

[CC BY-NC-SA 4.0](skills/mcpp-style-ref/LICENSE), 版权归 mcpp community. 这是本仓库里唯一不用 MIT 的 skill: 署名, 非商业使用, 改编后要用同样的许可证
