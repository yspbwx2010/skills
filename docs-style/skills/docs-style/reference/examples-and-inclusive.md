# Example data, inclusive language, and figurative language

Rules for the fictional values you put in examples, for words that exclude or hurt readers, and for idioms and metaphors that don't translate.

A rule marked "(skill rule)" is this skill's own and isn't in Google's guide.

## Contents

- [Example data](#example-data)
- [Keep the source's facts](#keep-the-sources-facts)
- [People and organizations in examples](#people-and-organizations-in-examples)
- [Gender and people](#gender-and-people)
- [Socially charged technical terms](#socially-charged-technical-terms)
- [Ableist and violent wording](#ableist-and-violent-wording)
- [Idioms, slang, and metaphors](#idioms-slang-and-metaphors)
- [Jargon and buzzwords](#jargon-and-buzzwords)
- [US-centric and culture-specific wording](#us-centric-and-culture-specific-wording)
- [Product names and trademarks](#product-names-and-trademarks)

## Example data

- Never use a real domain, email address, phone number, person, street address, or card number in an example. Use a reserved or fictional value, or a placeholder.
  - wrong: `Contact jane.smith@gmail.com` -> right: `Contact kai@example.com`
- Use `example.com`, `example.org`, or `example.net` for a generic domain. They are reserved for documentation.
  - wrong: `https://mycompany.com/api` -> right: `https://example.com/api`
- Build an example email address from a name on the approved list, or use a role address. Don't invent a person's name for it.
  - wrong: `john.doe@example.com` -> right: `luka@example.com`, or `support@example.net`
- Use IPv4 addresses from the three documentation blocks: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`. Use `2001:db8::/32` for IPv6.
  - wrong: `8.8.8.8` as an example public address -> right: `203.0.113.5`
  - Exception (skill rule): private ranges (`10.0.0.0/8`, `192.168.0.0/16`) are correct when the document is about private networking. The guide names only the three blocks listed earlier.
- For an example US phone number, pick one from the reserved `800-555-01xx` block.
  - wrong: `+1 415-555-0132` -> right: `800-555-0132`
- Avoid real street addresses. Use a clearly fictional one, such as 8 Rue du Nom Fictif, 341 Paris.
- Give an example project, host, or resource a meaningful name that fits the reader's setting. Don't use `foo`, `bar`, `baz`, or "dummy". Add a number when you need several (`production-1`, `production-2`).
  - wrong: `--project=foo` -> right: `--project=billing-staging`
- When every reader must supply their own value, use an uppercase placeholder instead of an invented value. When the source or the brief asks for an example value, use a realistic one and say that it's an example.
  - wrong: `--user-id=12345` -> right: `--user-id=USER_ID`
  - wrong: an example block that asks for a model alias and shows `MODEL_ALIAS` -> right: `model = "haiku"`, with a sentence that says the value is an example
- A secret in configuration or in a command gets a placeholder. Never use a real credential, token, or key, or a value that looks like one. The guide asks for fictitious values or placeholders and no personal data. The ban on lifelike secrets is this skill's own.
  - wrong: `token = "sk-live-4f9a..."` -> right: `token = "TOKEN"`

- A token in sample output gets a value in the real format, with an obvious example marker in it. Sample output means a log, a response, or a terminal transcript. A bare placeholder makes the output look unreal. Copy the format from the source. If the source gives none, mark the value as an example and say in the text that it's an example. This split is the skill's own. A brief that asks for sample output outranks the rule against invented output.
  - wrong: `Token: TOKEN` in a transcript of a successful sign-in -> right: `Token: tok_example_7f3k2q`

## Keep the source's facts

This section is this skill's own, not Google's. The example rules swap real or lifelike values for safe ones. They don't let you drop the facts that the example carries. The following cases come up most often:

- A concrete value that the source gives, such as an alias, a model name, or a path, stays unless it's personal data or a credential. Replace it with a placeholder only where each reader must substitute their own value.
- When you replace personal data, keep the shape of the value. An email address stays an email address, and an address stays in the same range.
- An address or range that the source states as a product fact, such as a default subnet, stays. Only addresses that serve as examples move to the documentation blocks. See [Example data](#example-data).
- Sample output keeps the fields, the order, and the date and time format that the product prints. The `YYYY-MM-DD` rule for sample data doesn't reformat a log line that the product writes another way.
- A legacy term that is a real identifier, an option name, or a quoted error message keeps its spelling in code font. See [Socially charged technical terms](#socially-charged-technical-terms).

## People and organizations in examples

- Draw first names from the approved list, and give a surname only as an initial. The approved names are:
  - Alex, Amal, Ariel, Bola, Charlie, Cruz, Dana, Dani, Hao, Ira, Izumi, Jie, Kai, Kalani, Kim.
  - Kiran, Lee, Lucian, Luka, Mahan, Noam, Nur, Quinn, Raha, Rosario, Sasha, Tal, Taylor, Tristan, Yuri.
  - wrong: `John Smith` or `Jane Doe` -> right: `Luka B.`
- Don't write Alice and Bob, or Eve and Mallory, unless the document describes a specification that uses them. When you do, keep the whole cast.
  - wrong: `Alice sends a token to the server.` (in a general tutorial) -> right: `Amal sends a token to the server.`
- Name a generic company "Example Organization". To tell two apart, add a descriptor: "Enterprise Example Organization", "Startup Example Organization".
  - wrong: `Acme Corp`, `Contoso` -> right: `Example Organization`
- Don't pair a role with a gender or an ethnicity as a stereotype. Vary names across roles.
- Use "they" for an example person, and say gender only when it matters.
  - wrong: `The admin signs in and he resets his password.` -> right: `The admin signs in and resets their password.`
- Write dates in sample data as `YYYY-MM-DD`, not in a US slash format (skill rule). Dates in running prose follow the date rules in the formatting reference.
  - wrong: `04/05/26` -> right: `2026-04-05`

## Gender and people

- Use a neutral term where one exists.
  - wrong: `8 man-hours` -> right: `8 person-hours`
  - wrong: `manpower`, `manned`, `manmade` -> right: `staff`, `staffed`, `artificial`

<!-- check-style: off -->

- Don't write "he or she", "(s)he", or "guys". Use "they", "you", or "everyone".
  - wrong: `Each user sets his or her password.` -> right: `Each user sets a password.`
- Use gendered pronouns only for a known individual.
- Avoid "man-in-the-middle". Write "on-path attacker" or "person-in-the-middle".
- Address the reader as "you". Keep "user" for the people who use what your reader builds.
  - wrong: `The user clicks Save.` (when you instruct the reader) -> right: `Click **Save**.`
- Don't use "we" or "let's" for the reader. "We" is fine when the authoring organization acts.

<!-- check-style: on -->

  - wrong: `Let's create a table.` -> right: `Create a table.`

## Socially charged technical terms

- Write allowlist and denylist (or blocklist, safelist) in new text. If readers might not recognize the new term, name the older term once, in parentheses, on first use. Then continue with the new term.
  - wrong: `Whitelist the IP address.` -> right: `Allow requests from the IP address.`
  - wrong: `Add the host to the blacklist.` -> right: `Add the host to the denylist.` (or "blocklist")
  - right, first use only: `Add the host to the denylist (older tools call it a blacklist).`
- Use allowlist, denylist, blocklist, or safelist as nouns only. Rewrite when you need a verb.

<!-- check-style: off -->

- Avoid master, and never pair it with slave. Don't use slave. Write primary, main, or controller for master, and worker or replica for slave.
  - wrong: `The master replicates to the slave.` -> right: `The primary replicates to the replica.`
- Keep a legacy term only when it is a real identifier, a keyword, or a quoted name. Put it in code font and introduce it once.
  - wrong: `The master key in the file names the node.` -> right: ``The `master` key in the file names the primary node.``
- Replace "grandfathered" with "legacy" or "exempt". Replace "blackhat" and "whitehat" with "illegal" and "legal" (or "unethical" and "ethical").
- Replace black-box and white-box testing with opaque-box and clear-box testing.

<!-- check-style: on -->

  - wrong: `Run a white-box test.` -> right: `Run a clear-box test.`

## Ableist and violent wording

<!-- check-style: off -->

- Don't use crazy, insane, lame, dumb, "dummy value", "sanity check", "blind to", or "cripple". State the actual property.
  - wrong: `Do a sanity check on the dummy value.` -> right: `Check the placeholder value.`
  - wrong: `The change crippled the service.` -> right: `The change slowed the service.` (add the measured slowdown only if the source gives it)
  - wrong: `The parser is blind to tabs.` -> right: `The parser ignores tabs.`
- Don't use "grayed out". Say "unavailable".
- Don't call people or systems "normal" or "healthy" in a way that implies others aren't. Use "typical", "responsive", or the exact measure.
  - wrong: `A healthy node answers requests.` -> right: `A responsive node answers requests.`
- Use person-first language by default: "people with disabilities". Follow the community's own preference where it differs. Don't write "suffering from", "wheelchair-bound", or "differently abled".
- Write "older adults", not "the elderly" or "seniors". Don't split readers by whether English is their first language.
- Avoid graphic or violent verbs. Use the plain technical verb.
  - wrong: `Kill the process, or nuke the cache.` -> right: `Stop the process, or delete the cache.`
  - Established terms with no better word stay: terminate and execute in their technical sense, and signal names in code font.
- Don't use "hang" for an unresponsive program.

<!-- check-style: on -->

  - wrong: `The server hangs on startup.` -> right: `The server stops responding on startup.`

## Idioms, slang, and metaphors

- Don't use idioms, slang, humor, pop-culture references, or sports metaphors. They fail in translation.
  - wrong: `This is a ballpark figure.` -> right: `This is an approximate figure.`
  - wrong: `hit the ground running` -> right: `start quickly`
- Replace out of the box (by default) and under the hood (internally).

<!-- check-style: off -->

- Replace these figurative phrases too (skill rule, no Google row): deep dive (detailed explanation), low-hanging fruit (name the easy items), silver bullet (single fix).
- Replace two more figurative phrases (skill rule, no Google row): boil the ocean (attempt too much) and bake in (build in).
- Prefer one precise verb over a phrasal verb: make use of (use), carry out (run), figure out (determine), look at (read), bring up (open). Set up and sign in stay as phrasal verbs, and so does log in when the product's UI uses it.
  - wrong: `The tool pulls in the dependencies.` -> right: `The tool installs the dependencies.`
- Don't use a figurative verb for software: falls back, gets to work, gives up, wants, asks, refuses.
  - wrong: `The client gives up on slow requests.` -> right: `The client times out on slow requests.`
- Don't end with an upbeat closer (skill rule).
  - wrong: `You're ready to go!` -> right: end at the last step, or give the next task
- Don't use metaphors for architecture: pets versus cattle, first-class citizen, native feature, single pane of glass.
  - wrong: `Treat servers like cattle, not pets.` -> right: `Treat servers as replaceable: re-create them instead of repairing them.`
- Don't use slang for people or events: ninja, guru, sherpa, war room, dojo, brown bag, shift left, white glove.

<!-- check-style: on -->

  - wrong: `Ask a Kubernetes guru.` -> right: `Ask an experienced Kubernetes administrator.`
  - wrong: `Hold a brown bag.` -> right: `Hold a learning session.`

## Jargon and buzzwords

- Try first to write around the jargon, then use a plainer word, and last define it where it first appears.
  - wrong: `Run a blast-radius analysis.` -> right: `Estimate which systems a failure can affect.`

<!-- check-style: off -->

- Avoid these words: actionable, agnostic, performant, native, traditional, off-the-shelf, learnings. Use "functionality" with caution.
  - wrong: `A performant model.` -> right: `An accurate model.` (or "a fast model", whichever is meant)
  - wrong: `Learnings from the migration` -> right: `What the team learned from the migration`
- Define "legacy", canary, workload, nonce, hot, warm, and cold failover on first use, or replace them.
- Don't use "spin up", "ingest", "surface", or "target" as verbs when a plain verb fits.
  - wrong: `Spin up a worker.` -> right: `Start a worker.`
- Say "mobile phone" or "mobile device", not "cell", "cellular", or "smartphone". Say "mobile data" or "mobile network".

<!-- check-style: on -->


## US-centric and culture-specific wording

- Don't name US shopping events or holidays as time markers. Name a month, or write "peak scale event".
  - wrong: `Plan for Black Friday traffic.` -> right: `Plan for peak traffic.`
- Write "US" for the country, never "America" or "American".
  - wrong: `American phone numbers` -> right: `US phone numbers`
- Don't use seasons or holidays for dates.
  - wrong: `Available in the summer.` -> right: `Available in July.`
- Don't rely on culture-specific names for diversity. The approved name list in "People and organizations in examples" is varied by design.

## Product names and trademarks

- For another owner's trademark, follow the owner's usage rules. The usual rule is to use the mark as an adjective before a noun, never as a verb.
  - wrong: `Photoshop the image.` -> right: `Edit the image in Photoshop.`
  - wrong: `Google the error.` -> right: `Search the web for the error message.`
- Leave a trademark exactly as its owner writes it: no plural, no possessive.
  - wrong: `Two Pixels` -> right: `Two Pixel phones`
- The project's own product name is exempt from the adjective rule, so "Relay starts" is fine. Spell it the same way every time, and don't alternate between it and "the app" or "the tool" for the same thing.
  - wrong: `Relay starts ... then the app reads ...` -> right: `Relay starts ... then Relay reads ...`
- Write product names in plain text, not in code font. Code font is for the command or file with that name.
  - wrong: ``Install `Docker`.`` -> right: `Install Docker.`

Source: adapted and condensed from the Google developer documentation style guide, https://developers.google.com/style, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Not affiliated with or endorsed by Google.
