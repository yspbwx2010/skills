# License notice

The `docs-style` skill is adapted from the following work:

- Title: Google developer documentation style guide
- Author: Google
- Source: https://developers.google.com/style
- License: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/

## Changes

This skill is an adapted and condensed version of the source. The rules are rewritten in new words, reordered, and merged. The `SKILL.md` file keeps mainly the rules that a baseline test showed models miss. The reference files cover a wider range of topics. The wrong -> right examples are original.

Some content is original work and doesn't come from the source:

- The "Write only the facts you were given" section of the `SKILL.md` file. The source doesn't cover invented facts.
- The "Framing" section of the `SKILL.md` file.
- The ranking of facts over style, and the four "Keep the source's facts" sections in the formatting, links and UI, examples, and API comments references.
- The order of precedence with project style, and the default exemptions for release notes and API reference comments.
- Word-list rows that the source doesn't have, such as "falls back" and "You're ready to go". The `SKILL.md` file lists the additions in its short table.
- A few smaller rules that the source doesn't state. Examples are a check that tells success from failure and one command per code block.

Some choices depart from the source. For example, the code-samples reference leaves the shell prompt (`$`) out of blocks that readers copy. The source shows the prompt on each input line of a multi-line block.

The following parts adapt Google material and aren't new work:

- `scripts/word_list.tsv`, the checker's data file, is derived from the Google word list.
- `reference/zh.md`, the Chinese supplement, applies several Google rules to Chinese. These rules cover headings, steps, placeholders, parallel lists, and numbers.

The checker's code in the `scripts/check_style.py` file is new. Its rules come from the source and from this skill.

No code samples from the source are included. The source publishes its code samples under the Apache 2.0 License, which doesn't apply here.

## No endorsement

This skill isn't affiliated with, sponsored by, or endorsed by Google. "Google" is a trademark of Google LLC, and its use here only identifies the source.

## License of this adaptation

This adaptation is also licensed under CC BY 4.0, https://creativecommons.org/licenses/by/4.0/. If you share or adapt it, credit the source that this notice names. Link to the license, and say what you changed.
