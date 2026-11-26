# docs-style

简体中文 | [English](README.en.md)

让你的 Coding Agent 按改编自 [Google 开发者文档风格指南](https://developers.google.com/style) 的规则写英文开发者文档: README, 操作步骤, 概念页和排障页, 发布说明, API 注释. 规则用自己的话重写过, 只留模型不看指南时还会犯的那些错

另附一份中文技术文档的补充规则. 默认的标点档案是我自己的半角写法 (也就是这份 README 的写法), 项目要求时可以换成主流的全角档案

## 优先顺序

- **事实先于风格**: 源材料里的事实 (错误信息, 界面位置, 平台列表, "可能" 这类限定语) 不会为了守哪条规则被删掉或改弱, 源材料里没有的说法不写
- **项目规矩和作者语气先于这个 skill**: 项目的风格文件, `AGENTS.md`, `CONTRIBUTING.md`, 以及作者自己的标点和语气说了算, 这个 skill 只补它们没管到的地方

## 它包含什么

- **主文件**: 优先顺序, 不编造事实, 说清谁在做动作, 同一个东西只用一个叫法, 列表和代码块的引导句, 编号步骤, 占位符, 句子和标题, 交付前的检查步骤
- **词表**: 该换掉的词和对应写法, 是一张表, 可以直接 `grep`
- **主题参考**: API 注释, 代码示例, 格式 (日期, 数字, 表格, 图片), 链接与界面, 示例数据与包容性用语, agent 按需读取
- **中文补充**: 两个标点档案, 中英文之间的空格, 术语, 数字与单位, 机翻腔和 AI 腔
- **检查脚本**: `scripts/check_style.py`, 只用 Python 标准库, 输出行号和规则名, 只报告, 从不改文件. 它只读英文 Markdown 正文, 中文文档按中文补充里的自检清单检查

## 效果

我让 LLM 当评审做了两轮盲评, 共 70 对, 每对是同一个任务带 skill 和不带 skill 各写一篇, 另外给 Haiku 的中文补测了 4 对. 带 skill 的文档在大多数配对里胜出 (第 3 轮英文 32 对里赢了 31 对), 编造的事实少得多 (35 处对 171 处). 风格问题也少得多 (42 处对 303 处), 不过这一项是按 skill 所依据的同一套规则打分的, 天然偏向 skill, 编造事实那一项更说明问题. Haiku 这类较弱的模型还是需要人工核对事实和篇幅, 中文尤其如此

## 安装

```bash
npx skills add yspbwx2010/skills --skill docs-style
```

或者 Claude Code 插件市场:

```text
/plugin marketplace add yspbwx2010/skills
/plugin install docs-style@yspbwx2010-skills
```

或者把 `docs-style/skills/docs-style/` 复制到 agent 的 skills 目录 (Claude Code 是 `~/.claude/skills/`)

## 许可证

改编自 [Google 开发者文档风格指南](https://developers.google.com/style), 原作以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 授权. 这份改编同样用 CC BY 4.0, 改了什么, 哪些是原创, 见 [LICENSE-NOTICE.md](skills/docs-style/LICENSE-NOTICE.md)

这个 skill 与 Google 没有隶属关系, 也没有得到 Google 的认可
