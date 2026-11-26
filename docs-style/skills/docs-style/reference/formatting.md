# Formatting

Detailed rules for source layout, paragraphs, headings, lists, procedures, tables, notices, dates, numbers, units, images, and other page elements. The most common failures (lead-ins, step structure, heading form) are also summarized in the main skill file. This file holds the full set.

## Contents

- [Decisions settled once](#decisions-settled-once)
- [Keep the source's facts](#keep-the-sources-facts)
- [Source layout](#source-layout)
- [Paragraphs](#paragraphs)
- [Headings](#headings)
- [Lists](#lists)
- [Procedures](#procedures)
- [Tables](#tables)
- [Notices](#notices)
- [Examples inside sentences](#examples-inside-sentences)
- [Italics and terms](#italics-and-terms)
- [Dates and times](#dates-and-times)
- [Numbers](#numbers)
- [Units of measure](#units-of-measure)
- [Images](#images)
- [Footnotes, math, and phone numbers](#footnotes-math-and-phone-numbers)

## Decisions settled once

- Prose in Markdown source: follow the repository. Look at two or three neighboring documents. If they wrap at 80 columns, wrap at 80. If each paragraph is one line, write one line. If there's no convention, write one paragraph per line and let the renderer wrap. Never rewrap text you aren't editing.
- Code and command lines wrap at 80 columns whatever the prose convention.
- Never put a line break inside a sentence in rendered output, and never use two trailing spaces or a `<br>` to force one.
- One H1 per document. Don't number headings. Use sentence case.
- A template that fixes the structure wins over the list and heading rules here. One example is a release-note template with Added, Changed, and Fixed groups.

## Keep the source's facts

This section is this skill's own rule, not Google's. Every rule in this file changes how you write a fact. None of them lets you delete one. When a rule and a fact collide, keep the fact and reword around the rule. The following cases come up most often:

- An error message in a heading: keep the message word for word. Put it in code font with a descriptive noun, or move it to the first sentence and keep the heading plain. A colon inside the quoted message doesn't make the heading a label-and-colon heading.
  - wrong: a heading reworded so that the message appears nowhere on the page -> right: ``## Fix the `cache: permission denied` error``
- A city, or a group of readers, tied to a time: keep the place and write the zone in full. See [Dates and times](#dates-and-times).
- A keyboard shortcut in a procedure: keep it in a sentence outside the steps. See [Procedures](#procedures).
- A list that the source marks as partial: introduce it with "such as" or "including". See [Lists](#lists).
- A time that the source writes in 24-hour form: convert it in prose. Converting the format keeps the fact, because 02:00 and 2 AM are the same time. So it doesn't conflict with the rule that facts outrank style. Keep 24-hour form where the guide allows it. See [Dates and times](#dates-and-times).

## Source layout

- Indent with spaces, never tabs. Use two spaces per level in Markdown, HTML, and YAML unless the file already uses another width.
  - wrong: a tab before a nested list marker -> right: two spaces
- Strip spaces from the ends of lines, apart from any that the Markdown syntax needs.
- Use Markdown unless the project already uses HTML. In an HTML file, use lowercase element and attribute names and write every closing tag. Pick elements by meaning: `cite` for a work title, `em` only for emphasis, `strong` only for importance. Use CSS for layout, never tables or `<br>`.
  - wrong: `<P CLASS="note">` -> right: `<p class="note">`
- Keep a URL on one line in source files, because a break inside it can stop the link from working. In rendered text, a break right after a slash is acceptable, and a hyphen inside the URL never is.

## Paragraphs

- Put one idea in each paragraph, with the most important point first. When a paragraph runs past five or six sentences, split it or cut it. A longer paragraph is fine if it holds a single idea.
- Skip a first sentence that only announces what follows. This skill's own rule, not Google's: the guide itself allows an opener such as "This document describes how to".
  - wrong: `This section explains how retries work.` -> right: `The client retries a failed request three times.`
- Vary how consecutive sentences start. Five in a row that begin with the same noun read as a list. Make it a list or recast two of them.
- Align text left only.

## Headings

- Use sentence case. Capitalize only the first word and the names of products and people.
  - wrong: `## How To Set Up A Proxy` -> right: `## How to set up a proxy`
- Start a task heading with a bare verb, not an -ing form. A few headings have no better option, such as Billing and Pricing.
  - wrong: `## Configuring the proxy` -> right: `## Configure the proxy`
- Write a concept heading as a noun phrase.
  - wrong: `## Indexing the archive` -> right: `## Archive indexing`
- Don't write a label-and-colon heading. The one exception is the Optional: prefix. The guide asks you to keep heading punctuation plain and doesn't name colons, so the ban is the skill's own narrower reading.
  - wrong: `## Fix: install bubblewrap` -> right: `## Install bubblewrap`
- A heading that quotes an error message keeps the message. See [Keep the source's facts](#keep-the-sources-facts).
- Don't number headings for sequence, and don't write "Step 1".
  - wrong: `### 1. Download the release` -> right: `### Download the release` (or, better, make it a numbered step)
- Keep punctuation plain. Don't end a heading with a colon, and avoid question headings.
  - wrong: `## Why does it fail?` -> right: `## Cause of the failure`
- Avoid repeating the document title in a heading.
- Don't skip levels.
  - wrong: `# Title` then `### Details` -> right: `# Title` then `## Details`
- Put text between a heading and its first subheading. The guide's rule is that every heading needs content under it, and its example uses an H2 and an H3. This skill applies the rule at every level, so an H1 followed directly by an H2 is an empty heading too.
  - wrong: `## Install` directly followed by `### Linux` -> right: `## Install` with one sentence, then `### Linux`
  - wrong: `# Get started` directly followed by `## Download the release` -> right: one sentence under the H1, then the H2
- Use real heading syntax, not a bold line.
  - wrong: `**Troubleshooting**` on its own line -> right: `## Troubleshooting`
- Don't put links in headings. Avoid code names too, and if one is unavoidable, add a noun.
  - wrong: ``## `--force` `` -> right: ``## Use the `--force` flag``
- Mark an optional section "Optional:" at the start, not "(optional)" at the end.
  - wrong: `## Add a proxy (optional)` -> right: `## Optional: Add a proxy`
- Introduce a group of subsections with "the following sections".
  - wrong: `This section covers three topics.` -> right: `The following sections cover three topics.`
- Keep an abbreviation out of a heading unless it's better known than its full form. If you use one, define it in the first paragraph under the heading. Skip the definition for terms that readers know, such as API, HTML, PDF, and URL.

## Lists

- Use a numbered list only when order matters. Otherwise use bullets.
  - wrong: `1.` `2.` `3.` for three unrelated options -> right: three bullets
- Don't make a list of one item. Write a sentence instead.
  - wrong: `### Fixed` followed by one bullet (outside a fixed template) -> right: one sentence
- In most cases, introduce a list with a full sentence. Usually, end it with a colon when the list follows at once, or with a period when other text sits in between. The items must not finish the sentence. If the heading directly before the list gives all the context, you can skip the introduction.
  - wrong: `Retries apply when:` -> right: `Retries apply in any of the following cases:`
- Keep items parallel where possible: all noun phrases, all imperatives, or all full sentences.
  - wrong: `- Faster startup` `- The cache is cleared on exit` -> right: `- Faster startup` `- Automatic cache clearing`
- Capitalize the first word of every item, except where case carries meaning, such as a list of command names.
- End an item with a period. Leave it off a single word, an item with no verb, and an item that is all code or all link text. If punctuation ends up mixed, recast the items to be parallel or punctuate all of them.
- Join a term and its description with a colon or a period, never a dash. After a colon, start in lowercase. After a period, start with a capital letter.
  - wrong: `**Cache** - stores results.` -> right: `**Cache**: stores results.` or `**Cache.** Stores results.`

<!-- check-style: off -->

- Use a serial comma, and don't end a list with "etc." or "and so on". If the source marks the list as partial, say so in the introduction instead.

<!-- check-style: on -->

  - wrong: `files, folders and so on` -> right: `Backups cover files, folders, and links.` when the source names all three
  - right, partial list: `Backups cover items such as files and folders.`
- In HTML, put multiple paragraphs in one item with `p`, not `br`.

## Procedures

- In most cases, start a procedure with a full sentence that adds context the heading lacks. An imperative lead-in such as "Install the tool:" works too. Usually, end it with a colon when the steps follow at once, or with a period when other text sits in between. Skip the sentence when the heading already says what the procedure does.
  - wrong: `Installing:` -> right: `To install the tool, do the following:`
- Write one action in each numbered step, and make sure the first sentence of the step includes an imperative verb.
  - wrong: `1. Download the file, verify it, and unpack it.` -> right: three steps
- The guide contradicts itself on a procedure with one step. Its procedures page asks for a one-item bulleted list, and its lists page forbids one-item lists. This skill writes the step as one plain sentence. Match the repository if it uses the bulleted form.
  - wrong: `1. Restart the service.` -> right: `To apply the change, restart the service.`
- Put the condition or location first, and the goal before the action.
  - wrong: `Run uname -m if you are unsure.` -> right: `If you are unsure, run uname -m.`
  - wrong: `Click **Save** to keep the changes, in the **Settings** dialog.` -> right: `In the **Settings** dialog, to keep the changes, click **Save**.`
- Order the parts of a step like this: action, command, placeholder explanation, a longer command explanation if needed, and output. Put the result or reason in a separate paragraph.
- State the result right after the action, in the same step. Add the reason when it matters. Name a result only if you know it from the product or the source.
  - wrong: `Click **Save**. You should see a confirmation.` -> right: `Click **Save**. A confirmation message appears.`
- Put a caveat before the step it affects, not after. The notices page makes the same point for prerequisites.
  - wrong: step 3 installs, then step 4 says "On WSL 1, this fails" -> right: the WSL 1 note comes before the install step
- Mark an optional step "Optional:" at the start, not "(Optional)".
  - wrong: `4. (Optional) Add a proxy.` -> right: `4. Optional: Add a proxy.`
- Use letters for sub-steps and lowercase Roman numerals for the next level down. In plain Markdown, indent a nested list instead.
- Avoid repeating a procedure. Link to it instead. When a task has several methods, document the one that most readers can complete.
- Don't give a keyboard shortcut as the way to do a step. If the reader must press the Enter key after typing, put both in the same step.
- If the source gives a shortcut, keep it in a sentence before or after the steps, and let the step name the menu action. The guide only says to leave shortcuts out of steps, so this placement is the skill's own.
  - wrong: `2. Press Control+comma.` -> right: `2. Select **Settings**.` plus the sentence `To open this window from the keyboard, press Control+comma on Linux and Windows (or Command+comma on macOS).`

<!-- check-style: off -->

- Use imperative verbs and no "please". Don't tell readers where something sits on the screen.

<!-- check-style: on -->


## Tables

- Choose by the shape of the data. Use a list for one attribute per item. Use a description list for a term and its description, or in some contexts a table. Use a table for three or more attributes.
  - wrong (in most contexts): a two-column Mode / Behavior table -> right: a description list: `**Strict**: rejects unknown keys.`
- Settled once for two-column tables: the guide says only "in some contexts" about a table for term and description pairs. It names reference pages only for one-row tables. This skill's reading: a two-column lookup table is fine in a reference page with many rows that readers scan by key. Anywhere else, use a description list.
  - wrong: a two-row "Time zone / Window" table in a notice -> right: one sentence that gives the window
- Don't add a table row that repeats a sentence next to the table. The guide has no such rule, and it's this skill's own.
- Turn a one-column table into a list. Avoid a one-row table, except in reference pages that keep one layout throughout. Never use a table for page layout, for code, or to split a long list into columns.
- Introduce each table with a full sentence, because not every screen reader announces a table. Say what the table holds.
  - wrong: a table right after a heading -> right: a lead-in sentence, then the table
  - right: `The following table lists the retry limits:`
- Avoid putting a table inside a numbered step.
- Write column heads in sentence case, short, with no end punctuation.
- Don't merge cells. Order rows logically, or alphabetically when no logic applies. Consider splitting a long table.
- Caption tables only when a document has more than one in close range: "Table 2. Retry limits" (sentence case, no period). From running text, refer to a table by number. The lead-in sentence can say "the following table".

## Notices

- Use few notices, and avoid putting two together. State information as normal text first.
- Pick the type by meaning:
  - Note: a useful, optional aside.
  - Caution: proceed with care.
  - Warning: stronger than a caution. The step is risky, can't be undone, or can lose data.
  - wrong: `Note: This deletes your data.` -> right: `Warning: This deletes your data and can't be undone.`
- Don't use a note for a prerequisite, a cross-reference, a fact the reader needs, an expected result, or a whole step. These limits apply to the note type only. A caution or warning exists to carry a fact the reader must have.
  - wrong: `Note: You need version 2.0 or later.` -> right: put the requirement in the prerequisites
- Don't let a heading stand in for a notice. The guide has no such rule, and it's this skill's own.
  - wrong: `### Security tradeoff` -> right: `Caution: This setting turns off the sandbox.`

## Examples inside sentences

- Avoid a semicolon before an example.
  - wrong: `Use a fast hash; for example, xxHash.` -> right: `Use a fast hash, such as xxHash.`
- At the end of a sentence, set off a short example with a comma, a dash, "such as", or "like". The guide marks a closing `(for example, ...)` as not recommended.
  - wrong: `Pass a flag e.g. --quiet.` -> right: ``Pass a flag, such as `--quiet`.``
- In the middle of a sentence, a short example can go in parentheses that start with "for example,".
  - right: ``Set a log level (for example, `debug`), and then restart the service.``
- A long example gets its own sentence that starts "For example,".

## Italics and terms

- Italicize a new term where you define it, once. Don't use bold or quotation marks.
  - wrong: `A "shard" is a slice.` -> right: `A *shard* is a slice.`
- Italicize a word used as a word.
  - wrong: `the word "or"` -> right: `the word *or*`
- Don't use bold for emphasis in running text. Bold marks UI labels and run-in headings only.
  - wrong: `**Minimal images** often omit shells.` -> right: `Minimal images often omit shells.`

## Dates and times

- Spell out month and weekday names, and give a four-digit year: month, day, year. Abbreviate only to save space in a heading or table, and then abbreviate the whole date.
  - wrong: `3/14/26` -> right: `March 14, 2026`
- A month with a year takes no comma. A full date in the middle of a sentence takes a comma after the year.
  - wrong: `the March, 2026 build` -> right: `the March 2026 build`
  - wrong: `the June 18, 2026 build` -> right: `the June 18, 2026, build`
- Write a date in numbers only when you must, and then use `YYYY-MM-DD`. The same form fits sample dates inside code and example data. If you can pick the sample, use a day above 12.
  - wrong: `23.09.2026` -> right: `2026-09-23`
- Put the date before the time: "June 18, 2026, at 9 AM".
- Use the 12-hour clock in prose, even when the source writes 24-hour times. Converting a time's format keeps the fact. Keep 24-hour time when the page documents a feature that uses it, or when it's required. When the UI, a command, or a code sample shows 24-hour times, write every time on the page that way.
  - wrong: `Maintenance starts at 02:00 and ends at 04:00.` -> right: `Maintenance starts at 2 AM and ends at 4 AM.`
- Write a 12-hour time with AM or PM in capitals after a space, and drop `:00`.
  - wrong: `9:00am` -> right: `9 AM`
- Avoid time zones. When one is necessary, give the region and a UTC offset, not an abbreviation. If the reader's own zone applies, you can say "your local time". If the product shows a zone format, use it.
  - wrong: `12 PM CET` -> right: `12 PM Central European Time (UTC+1)`
- Keep every city, region, and group of readers that the source ties to a time. The zone rule changes how you write the zone and never removes the place. The guide has no such rule, and it's this skill's own.
  - wrong: the source says "for readers in Seoul", and the text says only `11 AM Korea Standard Time (UTC+9)` -> right: `For readers in Seoul, maintenance starts at 11 AM Korea Standard Time (UTC+9).`
- Don't use seasons. Use a month or a quarter.
  - wrong: `shipped in spring` -> right: `shipped in April`
- Write a time range with a hyphen and no spaces. An en dash is wrong, and so is any space around the hyphen.
  - wrong: `20–30 seconds` -> right: `20-30 seconds`
- Don't mix a short and a long form in one date.

## Numbers

- Spell out zero through nine. Use numerals from 10.
  - wrong: `7 retries` -> right: `seven retries`
- Keep numerals below 10 for versions, technical quantities, steps, prices, math, and a number next to one above nine.
  - wrong: `five requests per minute` -> right: `5 requests per minute`
- Don't start a sentence with a numeral. Spell it out or recast.
  - wrong: `30 seconds is the default.` -> right: `The default is 30 seconds.`
- Write ordinals as words in text.
  - wrong: `the 3rd attempt` -> right: `the third attempt`
- Use commas from four digits, and a leading zero for decimals.
  - wrong: `4096 bytes`, `.5` -> right: `4,096 bytes`, `0.5`
- Write a range with a hyphen and no spaces, not an en dash.
  - wrong: `2019–2023` -> right: `2019-2023`
- Percent: numeral and sign, no space. At the start of a sentence, spell it out.
  - wrong: `75 %` -> right: `75%`
- Dimensions use a lowercase `x`, no spaces.
  - wrong: `64 x 64` -> right: `64x64`
- Use suspended hyphens in a series.
  - wrong: `a 5-minute, 10-minute, or 15-minute timeout` -> right: `a 5-, 10-, or 15-minute timeout`
- Avoid Roman numerals, except for sub-steps. Put the currency symbol first: `$25,000`. Add the country when it's unclear: `US$40`.

## Units of measure

- Separate a value from its unit with a space. Use a nonbreaking space where the markup allows, so the pair stays on one line.
  - wrong: `500MB` -> right: `500 MB`
- Exceptions: no space before `%` or a degree of angle (`90°`), and no space after a currency sign (`$20`).
- Write temperature with a space: `20 °C`. Kelvin takes no degree sign: `250 K`.
- Repeat the unit in a range, and join with "to".
  - wrong: `20 to 80 MB` -> right: `20 MB to 80 MB`
- Write rates with "per", not a slash, when space allows.
  - wrong: `calls/hour` -> right: `calls per hour`
- Use decimal units (kB, MB, GB) or binary units (KiB, MiB, GiB) to match what the technology measures. Hyphenate a compound unit: `node-hours`.
- Write thousands as `8k` only with a noun: `8k requests`.

## Images

- Show code and terminal text as text, so that readers can search it and screen readers can read it.
- Give every image alt text. A decorative image takes an empty `alt`.
  - wrong: `![](flow.svg)` -> right: `![Request flow from client to cache to database.](flow.svg)`
- Don't start alt text with "Image of", "Photo of", or "Picture of". Keep it to 155 characters, end it with punctuation, and avoid all capitals.
  - wrong: `![Screenshot of a graph of latency](latency.png)` -> right: `![Latency rising from 20 ms to 80 ms between 9 AM and 10 AM.](latency.png)`
- Say in text everything a diagram shows. The image must not be the only source.
- Write a caption as a full sentence with end punctuation: "Figure 1. A request moves from the client through the cache to the database." Refer to a figure by number, not as "the image above".
- Prefer SVG, then PNG, for diagrams. Use MP4 instead of an animated GIF.
- Avoid text inside images. If it's unavoidable, use words and short phrases, not sentences.
- Don't center images, and don't link to a figure on the same short page.

## Footnotes, math, and phone numbers

- Avoid footnotes. Use a cross-reference, a notice, or parentheses.
- Use a superscript for an exponent (`2<sup>3</sup>`), and a subscript for an index. Never write an exponent with a caret.
- Use italic for variables, and real symbols for minus, times, and not-equal in rendered math.
- Prefer a symbol (`a > b`) when the meaning is clear. Write a long equation on its own line.
- Write a fraction as a decimal when possible, or as hyphenated words (`three-sevenths`).
- Draw example US phone numbers from the 800-555-01xx block, which is reserved for examples and fiction. Never use a real number.
  - wrong: `415-555-1234` -> right: `800-555-0132`
- Write an extension as ", extension 204", not "x204".

Source: adapted and condensed from the Google developer documentation style guide, https://developers.google.com/style, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Not affiliated with or endorsed by Google.
