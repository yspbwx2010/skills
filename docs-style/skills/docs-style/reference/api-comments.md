# API reference comments

Rules for doc comments on public classes, functions, parameters, return values, errors, and deprecations. Tag syntax (`@param`, `///`, docstring sections) follows the project's tool. The wording rules below apply inside any syntax.

A rule marked "(skill rule)" is this skill's own and isn't in Google's guide.

## Contents

- [Scope and precedence](#scope-and-precedence)
- [Coverage](#coverage)
- [Classes, interfaces, structs](#classes-interfaces-structs)
- [Functions and methods](#functions-and-methods)
- [Parameters](#parameters)
- [Return values](#return-values)
- [Errors and exceptions](#errors-and-exceptions)
- [Deprecation](#deprecation)
- [Names and literals](#names-and-literals)
- [Write only what the code shows](#write-only-what-the-code-shows)
- [Keep the source's facts](#keep-the-sources-facts)
- [Final check for a comment block](#final-check-for-a-comment-block)

## Scope and precedence

The project's conventions come first, and reference comments relax some prose rules:

- The repository's comment convention wins: its tag syntax, density, and tone. Apply the rules below only where the convention is silent.
- Two prose rules from the main style rules are off in reference comments. One is the qualifying noun after every code name (`timeout`, not "the `timeout` key"). The other is contractions. Short member names and uncontracted negations are normal in reference text.
- Keep the passive-voice rule on: name the actor ("The function reports failures through the returned status") unless the actor is unknown or irrelevant.

## Coverage

Every public member needs a comment, and most need only one sentence:

- Describe every public class, interface, struct, enum, constant, field, typedef, function, parameter, return value, and error. Skip nothing because it looks obvious. One short sentence is enough.
  - wrong: `int retries;` (no comment) -> right: `/** The number of retry attempts after the first failure. */ int retries;`
- If you must not change the code, add comments only, and never split, reorder, or reformat a declaration to make room for one. When each enumerator or member sits on its own line, give each one a trailing comment (`///<` where the tool supports it). When the whole declaration is on one line, trailing comments are impossible: put one comment above the declaration and describe each enumerator or member inside it. This advice is the skill's own, because the guide leaves comment markup to the project's tool.
  - wrong: splitting `enum class Status { ... } status;` into a separate enum and a separate member, or breaking it across lines, so that each part gets its own comment -> right: one comment above the unchanged one-line declaration that says what each enumerator and `status` mean
- Keep member comments brief. One sentence is the default. Add a second only for a constraint the reader can't infer from the type.

## Classes, interfaces, structs

The first sentence of a class comment often appears alone in a list of classes, so make it short and specific:

- Open with the purpose, not the kind of thing, and skip openers like "This class" followed by a verb.
  - wrong: `/** This class represents a retry policy. */` -> right: `/** Decides how long to wait between failed attempts. */`
- Open with what the class does, not with its name.
  - wrong: `/** RetryPolicy decides when to retry. */` -> right: `/** Decides when a failed call is tried again. */`
- Keep the first sentence free of inner periods, so tools that cut at the first period show the whole sentence. Write "for example" with no abbreviation.
  - wrong: `/** Parses input, e.g. JSON. */` -> right: `/** Parses a JSON document into a tree. */`

## Functions and methods

The first sentence says what the function does, in present tense:

- Start with a present-tense verb that matches what the function does. For a getter, use the getter openers below instead of "Returns". In other descriptions, "Returns" is fine.
  - wrong (getter): `/** Returns the number of open sessions. */` -> right: `/** Gets the number of open sessions. */`
- Boolean getters start with "Checks whether".
  - wrong: `/** Returns true if the file is locked. */` -> right: `/** Checks whether the file is locked. */`
- Getters of any other type start with "Gets the".
  - wrong: `/** Returns the owner name. */` -> right: `/** Gets the owner name. */`
- Functions with no result start with "Sets", "Updates", "Deletes", "Registers", or the matching verb.
  - wrong: `/** Used to clear the cache. */` -> right: `/** Deletes every entry in the cache. */`
- A function that acts and also returns data starts with the action and mentions the data in the same sentence.
  - wrong: `/** Appends a record. Returns its ID. */` -> right: `/** Appends a record and returns its ID. */`
- Callback comments start with "Called by", then name the caller. Add what an implementation does only when the code shows it.
  - wrong: `/** Your handler. */` -> right: `/** Called by the server for each request. */`
- Put no behavior in the comment that the code or its caller documentation doesn't show (see "Write only what the code shows").

## Parameters

Each parameter gets one sentence with a capital letter and a period:

- Start with a capital letter and end with a period.
  - wrong: `@param name the user name` -> right: `@param name The name of the user.`
- Where it reads naturally, begin a parameter that isn't boolean with "The" or "A" ("An" before a vowel sound).
  - wrong: `@param timeout How long to wait.` -> right: `@param timeout The time to wait, in seconds.`
- For a boolean that tells the function to do something, describe both values.
  - wrong: `@param recursive Whether to recurse.` -> right: `@param recursive If true, includes subdirectories. If false, lists only the top directory.`
- For a boolean that states a fact about the object, use `True if ...; false otherwise`.
  - wrong: `@param visible Visible.` -> right: `@param visible True if the item is shown; false otherwise.`
- Write true and false as plain words, with no code font and no quotation marks, inside these sentences.
  - wrong: ``If `true`, includes ...`` -> right: `If true, includes ...`
- State a default as a separate sentence that starts with "Default:".
  - wrong: `@param limit The maximum count (defaults to 50).` -> right: `@param limit The maximum number of results. Default: 50.`
- Name units in the description when the type doesn't (skill rule).
  - wrong: `@param delay The delay.` -> right: `@param delay The delay before the first retry, in milliseconds.`

## Return values

Keep the return description short and put detail in the class or function description:

- If the value isn't a boolean, begin with "The". Name what the value is, not only its type.
  - wrong: `@return A UtilityOutcome.` (repeats the type) -> right: `@return The outcome of the call.`
- For a boolean, write `True if ...; false otherwise`.
  - wrong: `@return Whether it worked.` -> right: `@return True if the write succeeded; false otherwise.`
- Say each fact once (skill rule). Don't add a second block, such as an "error behavior" section, that repeats the return text.
  - wrong: a `@return` line, then an extra paragraph restating the same failure value -> right: one `@return` line that names the failure value.

## Errors and exceptions

Pick one opening for the whole project:

- Start an error description with "If" when the generator inserts "Throws" for you. Otherwise start with "Thrown when". Use one form per project.
  - wrong: `@throws IoError Error reading the file.` -> right: `@throws IoError If the file can't be read.`
- Settled once for the type after the tag: the slot right after `@throws` holds the name that the tool parses. Write it the way the tool expects, which is usually bare. The guide leaves comment markup to the project, and it says most generators set API names in code font and link them. In the description text, set every API name in code font.
  - wrong: `@throws NotFound If no Session has the given ID.` -> right: ``@throws NotFound If no `Session` has the given ID.``
- Describe the condition that triggers the error, not the error type again (skill rule).
  - wrong: `@throws NotFound NotFound is thrown.` -> right: `@throws NotFound If no session has the given ID.`

## Deprecation

A deprecation note points readers to the replacement:

- Start with "Deprecated." and name the replacement in the same note. If you track versions, say which version first deprecated the member.
  - wrong: `@deprecated Do not use.` -> right: `@deprecated Deprecated. Use fetch_all() instead.`
- When the replacement is an access path, say so.
  - wrong: `Deprecated. Obsolete.` -> right: `Deprecated. Read this value with the get_limit() function.`
- "Deprecated" means advised against, not removed. Write "removed" or "no longer works" only when that's true.

## Names and literals

Spell names and values the way the code does:

- Set every API identifier (class, function, constant, parameter) in code font, and link it to its reference page where the generator supports links.
  - wrong: `Calls the open method.` -> right: ``Calls the `open` method.``
- Set a string literal in code font and inside double quotation marks.
  - wrong: `Accepts 'strict' or 'lax'.` -> right: ``Accepts `"strict"` or `"lax"`.``
- Spell a class name exactly as in code, and never make it plural. Add a noun.
  - wrong: `Pass a list of Widgets.` -> right: `Pass a list of Widget objects.`
- Don't use a code name as a verb or add an ending to it.
  - wrong: `Lets you GET the status.` -> right: `Lets you send a GET request for the status.`
- Put a short sample (about 5 to 20 lines) at the top of each distinct reference page, not on every member.

## Write only what the code shows

Every rule in this section is the skill's own (skill rule). They target the most common failures in generated API comments. A reference comment states only what the code, its tests, or the author's notes confirm:

- Don't add ownership, lifetime, thread-safety, validity, or performance claims that aren't in the input.
  - wrong: `/** Takes ownership of the buffer and must stay valid until close. */` (when the code only reads it) -> right: `/** Reads from the buffer. */`
- Don't invent defaults, limits, or "always" and "never" guarantees.
  - wrong: `@return The path. Always set.` -> right: `@return The path, or an empty string if none is configured.` (only if the code does that)
- Don't describe polling, blocking, truncation, or encoding behavior from inference. If you must flag an inference, mark it for the author to verify.
  - wrong: `Must be cheap and must not block.` -> right: leave it out, or add a review note outside the comment.

## Keep the source's facts

This section is this skill's own, not Google's. The rules above shape a comment. They don't let you delete what the author or the code states. Keep the following when you reword:

- A guarantee that the source states, such as that a function doesn't throw or that a call is safe from several threads. Say it once, in the place the tag syntax gives it.
- A default, a unit, a limit, or a literal value. Use the `Default:` form and name the unit.
- Each error condition that the source lists. Give each one a line.
- Extra facts that don't fit the short first sentence. Put them in a second sentence instead of cutting them.
- The declaration. When the brief says not to change the code, the only edits are comments.

## Final check for a comment block

Before you finish a comment block, confirm each item:

- Every parameter, return value, and error has one line.
- The first sentence starts with a verb, not "This" or the name.
- Booleans state both outcomes.
- No sentence in the comment is a guess.
- Every guarantee, default, unit, and error condition from the source appears once.
- You left the declarations unchanged, and each API name in the description text is in code font.

The style checker doesn't check comment text inside fenced code, so use this list for doc comments.

Source: adapted and condensed from the Google developer documentation style guide, https://developers.google.com/style, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Not affiliated with or endorsed by Google.
