# Code samples, commands, and code in text

Rules for code blocks, shell commands, command output, placeholders, code font in prose, and file and file-type names.

## Contents

- [Decisions settled once](#decisions-settled-once)
- [Code blocks](#code-blocks)
- [Introducing a sample](#introducing-a-sample)
- [Shell commands](#shell-commands)
- [Command output](#command-output)
- [Command syntax notation](#command-syntax-notation)
- [Placeholders](#placeholders)
- [Code font in running text](#code-font-in-running-text)
- [Code elements in sentences](#code-elements-in-sentences)
- [Filenames and file types](#filenames-and-file-types)
- [Command-line terms](#command-line-terms)

## Decisions settled once

Don't reopen these decisions in each document:

- Leave the `$` prompt out of blocks that readers copy, and show input and output in separate blocks. Use a prompt only when one block must mix input with output, such as a transcript. Then start every input line with `$`, and don't offer the block for copying. A prompt breaks click-to-copy. The guide prefers a prompt on multi-line input, so this rule is a deliberate departure from it. If the project's documents use `$` everywhere, match them and stay consistent inside the document.
- Wrap code lines at 80 characters. Never break a URL, a string literal, or any token whose meaning changes when it's split. Leave a long line when wrapping changes the code.
- Don't hard-wrap prose unless the repository does. Prose follows the repository convention, and only code and commands wrap at 80 here.
- Use spaces for indentation, two per level, unless the language or the project says otherwise (Go, Makefiles, Python projects that use four spaces).

## Code blocks

- Use fenced blocks with a language tag. Tag shell commands `sh` (or `console` for a transcript). The code-samples page of the guide indents blocks by four spaces, and its syntax page uses fences. This skill follows the syntax page.
  - wrong: a bare fence around `npm ci` -> right: a fence tagged `sh` around `npm ci`
- Keep samples correct and runnable. Test a sample before you publish it, or say it's untested. That rule is the skill's own.
- Show a gap in code with a comment written in the sample's own language. Don't use `...` or the single ellipsis character, and don't offer a block with a gap for copying.
  - wrong: `routes:` newline `  ...` newline `  - path: /health` -> right: `routes:` newline `  # Other routes are omitted here.` newline `  - path: /health`
- Keep a prompt out of a block that readers copy. Line numbers and diff markers are the skill's own addition to that rule.
  - wrong: `1  npm ci` -> right: `npm ci`
- Use real formatting, not screenshots, for code and terminal text.

## Introducing a sample

- In most cases, introduce a block with a full sentence. End it with a colon when the block follows at once. End it with a period when a note, link, or other text sits between the sentence and the block. Skip the sentence only when the heading directly before the block gives all the context.
  - wrong: a bare heading "Example" followed directly by a block -> right: `The following command installs the dependencies:` followed by the block
- A fragment label isn't an introduction. Write a sentence, not "Fedora:" or "Instead:".
  - wrong: `Debian and Ubuntu:` -> right: `On Debian and Ubuntu, install the package:`
- Name the file in the sentence before a sample of its contents.
  - wrong: `Add the following:` -> right: `Add the following setting to the `config.toml` file:`
- Don't follow the sentence with a link and then a colon.
  - wrong: `The sample below uses the [API](/api):` -> right: `The following sample uses the API. For details, see [API reference](/api).`
- One sentence describing the action is enough for a command. Avoid "Run the following command:" and "by running the following command". Say what the command does.
  - wrong: `Run the following command:` -> right: `Build the image:`
- Don't use a position word for a block, such as "below" or "above". Use "following" or "preceding".

## Shell commands

- Put one command per block unless the commands run together as one step. That preference is the skill's own.
- Break a command longer than 80 characters with a trailing backslash preceded by a space. Indent the continuation lines four spaces. Break before an option, not inside a value.
  - wrong: one 120-character `curl` line -> right: `curl --fail --silent \` then `    --output release.tar.gz \` then `    https://example.com/releases/1.2.0/release.tar.gz`
- Make copyable examples run without edits, apart from placeholders. Leave out `[ ]`, `{a|b}`, and `...` syntax characters. To cover options, use one block per variant, or say in the introduction that more options exist and link the reference.
- Give one recommended way. Don't list alternatives unless the reader's situation requires a choice.
- Describe what a command does before naming its parts. Don't explain every flag.

## Command output

- Show output only when it helps: to confirm success, or to give a value the reader must copy. Don't show output for a command that prints nothing useful.
- Introduce it with "The output is similar to the following:". Use "The output is the following:" only when the output is exactly that text.
  - wrong: `You should see:` -> right: `The output is similar to the following:`
- Show the real output of a real run, not a guess. If the exact text is unknown, say what the reader checks for. When the brief asks for sample output, write it with an example marker in each secret value, as the examples reference describes.
  - wrong: `You should see `OK`.` (when the tool prints a checksum line) -> right: a block with the tool's actual line
- Mark omitted output with `...` alone on its own line.
  - wrong: `…` in the middle of output -> right: `...` on a line by itself
- Give a placeholder that appears in output an explanation. Use "This output includes the following values:" and the same list form as for commands. A token in output is no placeholder: see the secrets rule in the placeholders section.

## Command syntax notation

Use the following notation in reference pages that document a command's grammar, not in tutorials:

- Square brackets mean optional. Give each optional argument its own pair.
  - wrong: `tool build (optional) FILE` -> right: `tool build [FILE]`
- Braces and a pipe mean pick exactly one.
  - wrong: `tool mode json or yaml` -> right: `tool mode {json|yaml}`
- Three dots with no spaces between them mean the argument can repeat. A space before the dots is fine.
  - wrong: `tool add FILE (repeatable)` -> right: `tool add FILE [FILE ...]`
- Explain the notation once on the page if readers might not know it.

## Placeholders

- Write a placeholder in uppercase with underscores, and make the name descriptive. If the context makes that a bad idea, use another form and keep it consistent.
  - wrong: `--project=<your-project-name>` -> right: `--project=PROJECT_ID`
- Don't write angle brackets, lowercase names, hyphens, or mixed case.
  - wrong: `--region=my_region` -> right: `--region=REGION`
- Don't start a name with `YOUR_` or `MY_`.
  - wrong: `YOUR_API_KEY` -> right: `API_KEY`
- Don't use single letters or runs of `x` as placeholders. A run of `x` is fine where it's the standard, such as `2xx`.
  - wrong: `https://xxx.example.com/x` -> right: `https://HOST_NAME/PATH`
- A secret in configuration or in a command gets a placeholder. Never use a real credential or a value that looks like one.
  - wrong: `export API_TOKEN=sk-live-4f9a...` -> right: `export API_TOKEN=TOKEN`
- A token in sample output is the one exception: it gets a value in the real format with an obvious example marker. See [Examples and inclusive language](examples-and-inclusive.md#example-data).
- In running text, show a placeholder in code font and italic. Fenced blocks can't carry italics, so the uppercase form carries the signal there.
  - wrong: `Set PROJECT_ID to your project.` -> right: ``Set *`PROJECT_ID`* to the ID of your project.``
- Explain every placeholder at first use. For one placeholder, use a sentence after the block.
  - wrong: a block with `REGION` and no explanation -> right: ``Replace *`REGION`* with the name of the region that you use.``
- For two or more, put "Replace the following:" after the block and a bulleted list in order of appearance. Each item is the placeholder in code font and italic, a colon, and a lowercase description.
  - wrong: a table that explains the names in a different order -> right: `Replace the following:` then ``- *`PROJECT_ID`*: the ID of your project`` then ``- *`REGION`*: the region for the service``
- Repeat an explanation only where readers might miss it. Cases include a long document, a long procedure with many placeholders, and a document that isn't read in order.

## Code font in running text

- Use code font for anything that the reader types or that exists verbatim in code, on disk, or in output. That covers identifiers (classes, functions, attributes, elements, enums, packages), filenames, paths, environment variables, ports, and query parameters. It also covers HTTP methods, status codes, keywords, data types, commands, and literal values.
  - wrong: `Set the timeout attribute in config.yaml and call POST on port 8080.` -> right: ``Set the `timeout` attribute in the `config.yaml` file, and send a `POST` request to port `8080`.``
- Don't use code font for product names, service names, organization names, or domain names in prose. Don't use it for a URL for the reader to open. Make that a link.
  - wrong: ``Install `Docker` and visit `example.com`.`` -> right: `Install Docker and visit example.com.`
- Use code font for a domain or URL only when it's a literal inside code or a command.
- Put a plain noun after a code name so the sentence parses: the `model` key, the `--force` flag, the `serve` command, or the `Client` class.
  - wrong: `Set `model` before you start.` -> right: ``Set the `model` key before you start.``
  - Exception: reference comments and tables, where bare member names are normal.
- Name a method without its class unless the class prevents confusion.
  - wrong: ``Call its `session.close` method.`` -> right: ``Call its `close` method.``
- HTTP status codes: say "status code", and put the number and name in code font. For a group, write `2xx`.
  - wrong: `The server returns a 404 error.` -> right: ``The server returns an HTTP `404 Not Found` status code.``
- Booleans: code font for a value in data or code, plain font when you describe the result of a check.
  - wrong: ``Set `enabled` to True.`` -> right: ``Set `enabled` to `true`.``
- A command-line tool the reader runs is in code font. A project or product with the same name is plain.
  - wrong: ``The `curl` project ships `curl`.`` -> right: ``The curl project ships the `curl` command.``
- An email address is in code font when the reader types it or sees it in output. A contact address is a mailto link.
  - wrong: ``Write to `support@example.com`.`` -> right: `Write to [support@example.com](mailto:support@example.com).`
- If a UI label is also code (a name the user chose), use bold and code font together.
  - wrong: `Select staging-1 from the list.` -> right: ``Select **`staging-1`** from the **Cluster** list.``

## Code elements in sentences

- Never turn a code name into a verb, plural, or possessive. Add a plain noun and inflect that.
  - wrong: ```GET` the status.`` -> right: ``Send a `GET` request for the status.``
  - wrong: ```MAX_ITEMS`'s value`` -> right: ``The value of the `MAX_ITEMS` constant``
  - wrong: ``Two `Task`s run.`` -> right: ``Two `Task` objects run.``
- Use the standard signal names (`SIGTERM`, `SIGKILL`, `SIGINT`) in process-control text. Don't swap in "stop" or "cancel" for them.

## Filenames and file types

- Name a file in prose by putting its exact name in code font and adding the word "file". Copy a real filename character for character, whatever the naming conventions say.
  - wrong: `Open ~/.example/config.toml in an editor.` -> right: ``Open the `~/.example/config.toml` file in an editor.``
- Use the term that the context uses for a directory or folder. Without such a term, use "directory" for the command line and "folder" for a graphical file browser. When in doubt, use "directory".
  - wrong: `Open the config folder in the shell.` -> right: `Change to the configuration directory.`
- Name a file type the way people say it (a JSON file), not with its dotted suffix.
  - wrong: ``Upload a `.json`.`` -> right: `Upload a JSON file.`
- Use the verb "extract", not a file-type verb.
  - wrong: `Untar the archive.` -> right: `Extract the tar file.`

<!-- check-style: off -->

- Write "tar file", not "tarball". Write "filename" as one word.
  - wrong: `Download the tarball and check the file name.` -> right: `Download the tar file and check the filename.`
- Name new files in lowercase ASCII letters and digits, with hyphens between words, and with a name that says what is in them. Match a directory that already uses another style.
  - wrong: `Release_Notes.md`, `doc1.md` -> right: `release-notes.md`, `install-on-linux.md`
- Don't use an accented letter in a filename.
  - wrong: `creme-brûlée-recipe.md` -> right: `creme-brulee-recipe.md`
- Established names such as `README.md`, `LICENSE`, and `Dockerfile` keep their form.

<!-- check-style: on -->


## Command-line terms

- Use "flag" or the plain word "option" for command parts. Don't make the reader learn "metacharacter" or "positional argument" unless the page teaches them.
- Call the whole line a command, and a part with a leading hyphen a flag or an option. Pick one of the two words per document. The guide says "flag" for gcloud and "option" for Linux commands. Call a value given to a flag its value.
  - wrong: `Pass the verbose switch.` -> right: ``Pass the `--verbose` flag.``

Source: adapted and condensed from the Google developer documentation style guide, https://developers.google.com/style, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Not affiliated with or endorsed by Google.
