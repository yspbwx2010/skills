---
name: docs-style
description: Applies an adapted subset of the Google developer documentation style guide, plus a few rules of its own, to English developer docs. Covers READMEs, procedures, concept and troubleshooting pages, release notes, and API reference comments. Use when writing, editing, or reviewing developer docs or doc comments, or when asked for Google developer style. Project style rules and the author's own voice take precedence, and this skill fills only the gaps that they leave. Facts from the source outrank every style rule. Includes a word list, topic references, a Chinese supplement, and a checker script that reports problems without rewriting the file.
license: CC-BY-4.0
---

# Developer documentation style

Capable models make a predictable set of mistakes when they write developer documentation without a style guide. The rules here target those mistakes and skip what models already do well. For the full source, see the [Google developer documentation style guide](https://developers.google.com/style). Attribution is in the `LICENSE-NOTICE.md` file.

## Precedence

Among style rules, project rules and the author's voice come first. This skill fills only the gaps they leave. Before you write, look for a style file, an `AGENTS.md` file, a `CONTRIBUTING.md` file, or nearby documents in the same project. Follow what they set.

The following kinds of rules override this skill:

- A repository's comment rules, such as terse doc comments without contractions, or bare member names in reference comments.
- An author's punctuation and voice habits, such as no period at the end of a Chinese paragraph, or a house tone for pull request text.
- A product's UI wording. If the button says **Log in**, then the docs say "log in", even though this skill prefers "sign in".
- A required template, such as a release-note template with fixed Added, Changed, and Fixed groups.

Two exemptions apply by default:

- Release notes can use "now", "new", and "no longer", and can have a group with one item.
- API reference comments follow the repository's convention for contractions and for bare member names.

Facts outrank every style rule, whether it comes from this skill or from the project. This ranking is this skill's own, not Google's. Source facts include error messages, UI locations, place names, and lists of platforms. If a rule asks you to delete or change such a fact, keep the fact and reword around it.

For documents in Chinese, read the [Chinese supplement](reference/zh.md). Use the supplement instead of the sentence rules that only fit English, such as contractions. The facts rules and the fact and length steps of the final pass apply to Chinese documents in full. The only step skipped for Chinese is running the checker, because it can't read Chinese punctuation.

## Before you draft

Each reference file covers one area. Before you draft, open each reference whose trigger matches the brief or the source:

- **Doc comments in source code**, such as `@param` or `///` lines: [API comments](reference/api-comments.md). It covers parameter and return forms, boolean wording, exceptions, deprecation, and a final check for comment blocks.
- **Commands, code blocks, command output, or placeholders**: [Code samples](reference/code-samples.md). It covers line length, line continuation, output blocks, the shell prompt (`$`), and omitted code.
- **Dates, times, time zones, numbers, units, tables, notices, or images**: [Formatting](reference/formatting.md). It also covers lists, procedures, headings, footnotes, and math.
- **Buttons, menus, dialogs, panes, keyboard keys, or links**: [Links and UI](reference/links-and-ui.md). It covers UI element names, menu paths, key names, link text, and anchors.
- **Example people, email addresses, domains, IP addresses, tokens, or sample output**: [Examples and inclusive language](reference/examples-and-inclusive.md). It also covers inclusive and figurative language.
- **A word you aren't sure of**: the [word list](reference/word-list.md). The word-list section later in this file shows how to search it.
- **A document in Chinese**: the [Chinese supplement](reference/zh.md).

Wrap prose source the way the project does. For the `$` prompt, the code-samples reference sets a default, and the project's own convention overrides it.

## Write only the facts you were given

This section is this skill's own rule, not Google's. Invented facts were the most serious problem in testing, and style rules can't fix a wrong fact.

Don't add the following kinds of claims unless the source states them:

- Behavior, defaults, limits, ownership rules, or threading rules. "The callback must be cheap and must not block." -> leave it out, or ask the author.
- Causes and environments. "Some container runtimes also block user namespaces." -> list only the causes that you were given.
- Guarantees and safety claims. "The struct is safe to log." -> "The struct doesn't hold provider error text." (only if the source says so)
- Performance or quality claims. "This makes startup faster and less intrusive." -> "Startup skips the plugin scan." (only if the source says so)
- Expected output that you haven't seen. If you don't know the exact output, describe what to check, or ask for a real sample. If the brief asks for sample output, write it and mark each secret value as an example.

If you need an inference to finish a sentence, list it separately for the author to confirm. Don't write it as fact.

Keep the source's hedges. If the source says that an upload "might take longer", don't write "takes longer" or "you'll notice a delay".

If the facts run out before the length that the brief asks for, end the document there. Tell the author how many words short it is. Don't add claims to reach a word count.

Security features help. They don't guarantee. "The sandbox prevents steps from reading your keys." -> "The sandbox helps protect your keys."

## Name the actor

Say who or what does each action. Check API comments most closely.

Fix these patterns:

- **Passive voice.** "Failures are reported through the returned status." -> "The function reports failures through the returned status."
- **An -ing form as the subject.** "Starting the server fails with the following error:" -> "When you start the server, it fails with the following error:"
- **Human verbs for software.** "The engine refuses to start." -> "The engine doesn't start."

Replace human verbs with these plainer verbs:

| Human verb | Use instead |
|---|---|
| asks you to | prompts you to |
| refuses to | doesn't |
| wants, needs | requires |
| tells you, lets you know | shows, reports, indicates |
| knows | stores, has |

Passive voice is fine when the actor is unknown or doesn't matter, as in "The file is created at install time."

## Use the same word every time

Writers vary words on purpose to avoid repetition. In technical writing, repetition is correct, because a new word reads as a new thing. For example, don't call one file "archive", "download", and "tarball", and don't switch from the product name to "the app".

Pick one term for each concept. Prefer the name that the code or UI uses. If a struct field is named `response`, write "response" every time. One term doesn't mean one sentence pattern: keep the noun. The advice to vary how the sentences open is this skill's own.

Make every "it" and "its" point to one noun. "The client calls the helper and logs its output." -> "The client calls the helper and logs the helper's output." If the referent is already clear, keep "it".

## Put a noun after a pointer

A pointer word without a noun can leave the reader guessing. Usually, add the noun. If the noun makes the sentence clumsy, leave it out, but make sure the reader can still tell what the word points to.

Fix these patterns:

- **"this" or "these" with nothing clear to point to.** Here the noun is required. "Use this for short background tasks." -> "Use this function for short background tasks." If the noun fits more than one thing nearby, use the name instead. "When this function returns false, `upload` stops." -> "When `should_continue` returns false, `upload` stops."
- **"the following" before a block.** The noun is optional after "the following". Add it when it makes the target clearer or helps screen-reader users. "Add the following to `settings.toml`:" -> "Add the following lines to the `settings.toml` file:"
- **A bare file name.** "Open `~/.example/settings.toml` in an editor." -> "Open the `~/.example/settings.toml` file in an editor."
- **A bare key, flag, or command.** "Set `timeout` to `30`." -> "Set the `timeout` key to `30`."

In API reference comments, follow the repository's convention for bare member names.

## Introduce lists, procedures, and code blocks

In most cases, put a complete sentence before a list, a procedure, or a code block. Skip it for a list or procedure when the heading right above already gives all the context. Don't write a lead-in that only repeats the heading.

Usually, end the sentence with a colon when nothing sits between it and the list or block. If a note comes in between, end with a period. Either way, the sentence must make sense without the colon.

Fix these patterns:

- **A fragment before a list.** "This usually happens in:" -> "This error appears in the following environments:"
- **A one-word label.** "Instead:" -> "Instead, use the following command:"
- **A command without its purpose.** "To confirm the installation, run:" -> "To confirm the installation, check the version:"
- **A platform label before a block.** "Debian or Ubuntu:" -> "On Debian or Ubuntu, install the package:"
- **A heading that doesn't explain the procedure.** Under "## Models", step 1 starts at once -> "To set the default model, follow these steps:"
- **A file sample that doesn't name the file.** A TOML block after "Behavior is unchanged." -> "The following `settings.toml` file sets a two-minute timeout:"

## Write procedures as numbered steps

Use a numbered list for any sequence of two or more steps that the reader performs. Don't write a procedure as headings and paragraphs.

Follow these rules:

- **One step, no list.** Write a one-step procedure as one sentence. "1. Run `make install`." -> "To install the tool, run `make install`." Google's pages disagree on this case, so this choice is the skill's. A repository that uses a one-item bulleted list wins.
- **One action per step.** Don't number headings to show order. "### 1. Download the release" ... "### 2. Verify it" -> one numbered list under "Install the CLI".
- **Condition first.** "Run `uname -m` if you're not sure of your architecture." -> "If you're not sure of your architecture, run `uname -m`."
- **Show the result when it helps.** "You should see `OK`." -> "The output is similar to the following:", then a block with the real output. If you don't have the real output, follow the rule in the facts section.
- **A check that can tell success from failure.** "Confirm that the command returns a reply." can't tell the configured backend apart from the fallback. Name the signal that differs.
- **Caveats before the step.** The note that the steps don't work on WSL 1 goes before step 1, not after the commands.
- **One recommended path.** Drop "To install system-wide instead, ..." unless the reader asked for options. Troubleshooting docs can give a requested opt-out.
- **No key commands in parentheses.** "Convert the distribution (`wsl --set-version DISTRO_NAME 2`)." -> put the command in its own block with its own lead-in. The guide has no such rule, and it's this skill's own.

## Placeholders

Write each placeholder in uppercase with underscores. Don't use angle brackets, and don't add "your" or "my".

Fix these patterns:

- `wsl --set-version <distro> 2` -> `wsl --set-version DISTRO_NAME 2`
- `cd your-project` or `cd ~/src/my-project` -> `cd PROJECT_DIRECTORY`
- `export YOUR_API_KEY=...` -> `export API_KEY=...`

Explain every placeholder after the block. In running text, a placeholder is in code font and italics. For one placeholder, write "Replace *`DISTRO_NAME`* with the name of your distribution." For two or more, write "Replace the following:" and a list in order of appearance. For more about placeholders and samples, see [Code samples](reference/code-samples.md).

Google allows either an invented example value or a placeholder. This skill chooses between them as follows:

- **An example value when the brief asks for an example.** Write a realistic value, such as `name = "demo-project"`, and say that it's an example.
- **A placeholder when every reader must supply their own value**, such as a key, a path, or an account ID.
- **A placeholder for the whole value.** "Download `ARCHIVE.tar.gz`. Replace `ARCHIVE` with the filename." invites a doubled extension. -> `ARCHIVE_FILE`, explained as the full filename.

## Sentences

Apply these sentence rules:

- **Contractions in guides.** "The file does not exist." -> "The file doesn't exist." Exempt reference comments if the repository writes them without contractions.
- **Sentence length.** Keep a sentence to 25 words or fewer. Split a long sentence at its second idea.
- **Few semicolons.** Where you can, write two sentences instead.
- **"can" for options, "might" for possibility, "must" for requirements.** "The provider may return an empty reply." -> "The provider can return an empty reply."
- **No "should" or "will" for plain facts.** "The value should be 30." -> "The value is 30." "This call will return a list." -> "This call returns a list." Keep "will" for a real later event. For advice, write "we recommend".
- **Helper words.** Add "then" after an "if" clause, especially a long or complex one, because it shows where the condition ends. "If the file is missing, the cache is empty, and the flag is off, the tool stops." -> "..., then the tool stops." The guide's recommended examples add it after short clauses too: "If the cache is stale, the tool rebuilds it." -> "If the cache is stale, then the tool rebuilds it." This skill's own reading: a short imperative can skip it, as in "If the cache is stale, rebuild it."
- **Keep "that".** "the model you want to use" -> "the model that you want to use"
- **"only" before the word it limits.** "You only need to run it once." -> "You need to run it only once."
- **after, because, although.** "Once you're signed in" -> "After you sign in". "Since the cache is stale" -> "Because the cache is stale". Use "although", not "while", for contrast.
- **One verb, not a phrasal verb or idiom.** "falls back to the default" -> "uses the default". "pulls in the dependencies" -> "installs the dependencies". Keep "set up" and "sign in", which have no one-word form. Use "log in" only when the product's UI says it.
- **Expand unfamiliar abbreviations and gloss jargon on first use.** "WSL 1" -> "*Windows Subsystem for Linux* (*WSL*) 1". Common ones such as API, URL, and HTML rarely need it. Gloss a term such as "turn" or "code point" the first time it appears.
- **Parallel list items.** Don't mix noun phrases and sentences in one list. "Shorter request timeout." next to "Your titles are kept." -> make both items noun phrases or both items sentences.

## Headings

Use these heading forms:

- **Sentence case.** "# Release Notes for 0.4.0" -> "# Release notes for 0.4.0"
- **A bare verb for task headings.** "## Fix: install the helper" -> "## Install the helper". "## Installing the helper" -> "## Install the helper".
- **A noun phrase for concept headings.** "## What happens if the model isn't available" -> "## Fallback when the model is unavailable"
- **Plain punctuation.** Rewrite a label-and-colon heading as a plain heading. The one exception is the `Optional:` prefix, as in "## Optional: Add a proxy".
- **Error messages kept whole.** A heading that quotes an error message keeps the message, colon included. Put it in code font with a noun, as in "## Fix the `quota exceeded: disk full` error". Or keep the heading plain and quote the full message in the first sentence.
- **No numbers and no bold lines.** Don't fake a heading with a bold line such as "**Fedora**". Don't bold words for emphasis either.
- **Text between levels.** Put at least one sentence between a heading and its first subheading. This skill's own reading: the page title counts too, so don't follow the H1 directly with an H2.

## Framing

The rules in this section are this skill's own, not Google's. Cut these framing habits:

- **"This page" openers.** "This page shows you how to set up the CLI." -> start with the task: "To set up the CLI, follow these steps:". Google's own examples accept "This document shows you how to ...", so keep that form where the project uses it.
- **Padding at either end.** Cut a three-part summary lead, such as "This release adds X, tightens Y, and improves Z." Cut an upbeat closer, such as "You're ready to go." Add a "Next steps" section only when the brief or the project template asks for one.
- **Consequence tails.** "..., making it harder for attackers to hide commands." -> drop the tail, or state it as a separate sourced fact.
- **Unsourced hedges.** "Most distributions already include `~/.local/bin`." -> "If `~/.local/bin` isn't in your `PATH` environment variable, add it." A hedge that the source gives stays, as the facts section says.
- **Vague claims.** "Title generation is faster." -> "Title requests time out after 15 seconds." (only if the source says so)

## Word list

Replace these words in prose:

| Avoid | Use |
|---|---|
| config | configuration |
| repo | repository |
| tarball | tar file |
| log in | sign in (unless the UI says "log in") |
| type (text into a field or prompt) | enter |
| access (as a plain verb) | read, see, edit, use |
| hang, hung | stop responding |
| read only | read-only |
| file name | filename |
| non-interactive | noninteractive, unless the document consistently uses the hyphen |
| trade-off | tradeoff |
| this page | this document |
| above, below (for position) | preceding, following, earlier, later |
| currently, from now on, in the future | delete the phrase, unless the source contrasts times |
| new, existing | delete the word ("Create a project"), unless the source contrasts new with existing |
| falls back, pulls in, gets to work | one verb, such as "uses" or "installs" |
| You're ready to go | delete the sentence |
| safe, prevents, ensures (security) | helps protect |
| simply, just, easy, easier | delete the word |

A few entries are this skill's additions, not Google's: "from now on", the phrasal-verb row, and "You're ready to go". For other *non* words, Google leaves the hyphen to judgment. Both "nonprinting" and "non-printing" are acceptable, so pick the more readable form and use it every time. Prefer the closed forms that the guide lists (noncurrent, nonempty, noninteractive, nonpublic), unless the document consistently uses another form. The checker reports a hyphen in these four only at `--info`.

For every other word, search the [word list](reference/word-list.md). The file is a table, so grep works from the skill folder, as in `grep -i '^| whitelist' reference/word-list.md`.

## Final pass

Before you hand the document back, follow these steps:

1. Run the checker on each changed English Markdown file. It doesn't read Chinese punctuation, so skip Chinese files. From the skill folder, run the following command:

   ```sh
   python3 scripts/check_style.py path/to/document.md
   ```

   The checker reports line numbers and rule names. It never edits the file. Run `python3 scripts/check_style.py --help` for options.

   The checker reads only Markdown prose. It doesn't check comment text inside fenced code, so it can't check doc comments. For comments, use the final check in the [API comments](reference/api-comments.md) reference instead. Don't add a prose lead-in to a file that holds only code.

2. Fix each finding that applies. Skip a finding when a project rule or an exemption in the precedence section covers it. Never delete or weaken a source fact to clear a finding.
3. Run the checker once more with `--info`. Fix each "now", "new", or passive hit that doesn't come from the source. For an `if-then` hit, consider adding "then". This skill leaves a short imperative as it is.
4. List the nouns for each main object in the document. Collapse any synonyms to one term.
5. Compare each claim with the source. In your reply, list every claim that you deleted or flagged. If you list none, say so, and name the source fact behind each sentence that states behavior.
6. Check the other direction. Confirm that each source fact still appears with its original strength, especially error messages, UI locations, places, platforms, and hedges. In your reply, name any fact that you left out, and say why.
7. Confirm that each list, procedure, and code block has a full-sentence lead-in, unless the heading right above already gives the context.

## Attribution

This skill adapts and condenses the [Google developer documentation style guide](https://developers.google.com/style), which Google publishes under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/). The rules are rewritten, reordered, and cut down. The wrong/right examples are original. Some parts are this skill's own work, not Google's. They include the facts section, the ranking of facts over style, and the framing section. They also include the default exemptions, the word-list additions, and other rules marked as this skill's own. This skill isn't affiliated with or endorsed by Google. For details, see the `LICENSE-NOTICE.md` file.
