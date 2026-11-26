# Word list

Lookup table for word and phrase choices in developer documentation. One row per term. Search it with grep, for example `grep -i -n "^| tarball" word-list.md`, or `grep -i "sign in" word-list.md` to see every row that mentions a phrase.

## Contents

- [How to read the table](#how-to-read-the-table)
- [Terms, alphabetical](#terms-alphabetical)

## How to read the table

Each row has three cells, and a few conventions apply:

- term: the word or phrase as it might appear in a draft.
- guidance: what to do, in short.
- use instead: the replacement. A dash means you need no replacement: follow the guidance.
- skill row: a guidance cell that starts with these words marks a term Google's list doesn't cover. The skill added it, so don't present it as Google's rule.

<!-- check-style: off -->

- Precedence: when the product's own UI or the project's documents use a term (for example "log in" on a button), follow them. The table applies to words you choose yourself.
- Facts first (skill rule, not Google's). A "drop" in the last cell applies only when the word carries no fact. Suppose the word marks a contrast, a date, a version, a place, or a quoted message. Then keep the fact and reword around the word.
- Hot terms: the ones drafts hit most often are config, tarball, log in, type, access, this page, trade-off, and hang. Also watch above, below, then, should, and future-tense or "new" wording.

<!-- check-style: on -->


## Terms, alphabetical

The table lists the words to avoid, so the style checker skips it.

<!-- check-style: off -->

| term | guidance | use instead |
|---|---|---|
| & | avoid in prose, headings, nav; ok in UI labels, tight tables, code | and |
| + | ok after numbers in casual text (300+); not formal | - |
| -aware | avoid as compound modifier | - |
| a / an | choose by sound, not letter | - |
| A/B testing | caps with slash | - |
| abnormal | avoid for people; ok for system state | - |
| abort | avoid in general prose | stop, exit, cancel, end |
| about vs on | cross-reference that names the topic: use about | "more information about X" |
| above | don't use for document position, version range, or UI position; ok for hierarchy. For a UI position, name the container instead and keep the fact | earlier, preceding, later |
| access (verb) | avoid when a plainer verb fits | read, see, edit, find, use, view |
| account name | don't use | username |
| actionable | avoid | useful, "that you can act on", or drop |
| ad hoc | ok for free-form queries; no hyphen or italics | - |
| ad tech | expand on first use; not adtech | advertising technology (ad tech) |
| address bar | the browser's URL box; omnibox is not a general term | address bar |
| admin | spell out unless UI label | administrator |
| agnostic | don't use | platform-independent |
| AI | ok without expansion unless the audience is unfamiliar | - |
| aka | don't use | also known as, or parentheses |
| allowlist | ok as noun; not as verb | rewrite the sentence |
| allows you to | don't use | lets you |
| alpha | lowercase unless product name | - |
| AM, PM | caps, no periods, space before; drop :00 on a round hour | 3:45 PM, 3 PM |
| America, American | only for the continents; not for the US | US, United States |
| and so on | avoid | including, such as |
| and/or | avoid except in tight tables | - |
| anti-pattern | avoid esp. in headings | specific description |
| API | web or language API; not for a single method or class | - |
| app | prefer to application for end-user software | - |
| appendix | plural appendixes | - |
| application | keep in fixed phrases like application programming interface | - |
| as (reason) | avoid | because |
| as of this writing | avoid, timeless docs | drop |
| auth(N/Z) | don't use abbreviations | authentication, authorization |
| authenticate | use against, not to | - |
| authenticated vs authorized | authenticated = user; authorized = request on behalf of user | - |
| auto* | closed compounds (autoscaling, autopopulate) | - |
| autoupdate | don't use | automatically update |
| backend | one word | - |
| bake in | skill row: figurative | include, build in |
| ballpark | idiom | approximate |
| bar | avoid as placeholder | clearer name |
| bare metal | lowercase; hyphen as modifier | - |
| base64 | lowercase; code font only for literals | - |
| baz | avoid as placeholder | clearer name |
| below | don't use for document, version, or UI position; ok in set phrases like below zero. For a UI position, name the container instead and keep the fact | later, following |
| best effort | avoid | specific wording |
| beta | lowercase unless product name | - |
| between vs among | between = distinct items; among = group or non-distinct | - |
| big-endian | hyphen, lowercase | - |
| Black Friday | avoid unless the US event | peak scale event |
| black-box | avoid | opaque-box testing, synthetic monitoring |
| blackhat | don't use | illegal, unethical |
| blackhole (verb) | don't use | dropped without notification |
| blacklist | don't use | denylist, blocklist, excludelist |
| blast radius | don't use | affected area |
| blind | avoid figurative use | ignore, unaware of, without confirming |
| blue-green | hyphen, not slash | - |
| boil the ocean | skill row: idiom | attempt too much |
| boolean | code font when the type keyword; lowercase abstract; Boolean logic caps | - |
| break-glass | don't use | emergency access, manual fallback |
| bring up | skill row: phrasal verb | open, start, raise |
| brown bag | don't use | learning session |
| build cop | don't use | build monitor |
| button | refer to it by its label; never use for a link or a menu item | - |
| can | ability, permission, option, possible outcome | - |
| canary | avoid; define if used; not as verb | - |
| careful, carefully | avoid | state the concrete check |
| carry out | skill row: phrasal verb | run, perform |
| cell phone | don't use | mobile phone, phone |
| cellular data | don't use | mobile data |
| cellular network | don't use | mobile network |
| chapter | only in books | document, page, section |
| check (checkbox) | don't use | select |
| checkbox | one word | - |
| choose | ok generic; select for UI | - |
| clear (checkbox) | use for unchecking | - |
| CLI | don't use generically | name the tool |
| click | desktop mouse; no "click on"; hyphenate right-click | - |
| click here | don't use | descriptive link text |
| client | short for client app in API docs; not for library | library |
| client ID | lowercase | - |
| client secret | lowercase | - |
| co* | closed compounds | - |
| codebase | one word | - |
| cold (failover) | avoid jargon or define | - |
| colocate | no hyphen | - |
| compliant | use with caution; strong claim | - |
| comprise | don't use | consist of, contain, include |
| confidential | data protected from unauthorized access | - |
| config | avoid in prose | configuration |
| cons | don't use | disadvantages |
| content type | only for Content-Type header context | media type |
| Control+S | Control+KEY; both OS if mixed audience; no Ctl/Cmd | - |
| copy and paste | avoid | say what to enter |
| could | avoid | can |
| CPU | caps, no expansion | - |
| crazy | don't use | complicated, unexpected |
| Create a new | avoid | Create a |
| cripple | don't use | slowed, specific |
| cross-site request forgery | lowercase | - |
| curl | lowercase | - |
| currently | avoid: the word is implied. Keep the fact if it limits something, and give a version or date | drop |
| Cyber Monday | avoid unless US event | peak scale event |
| dash | don't call hyphen a dash | - |
| data | singular mass noun | - |
| data center | two words | - |
| data cleaning | cleansing is the wrong word | data cleaning |
| data flow | two words unless stream processing sense | - |
| data source | two words | - |
| data type | two words | - |
| datastore | one word | - |
| DDoS | hyphenate expansion; DDoS after | - |
| dead-letter queue | define on first use | - |
| deep dive | skill row: idiom | detailed explanation |
| deep linking | no hyphen | - |
| deficient | ok for systems, not people | - |
| demilitarized zone | don't use | perimeter network |
| denigrate | don't use | disparage |
| denylist | ok noun; not verb | - |
| deprecate | means advise against; not removed | - |
| deselect (checkbox) | don't use | clear |
| desire, desired | don't use | want, need |
| DevOps | no expansion needed | - |
| dialog | UI element; dialogue = speech | - |
| directory vs folder | use the term the context uses (directory in a CLI, folder in a GUI); when unsure, directory | - |
| disable | avoid for broken things | inactive, unavailable, turn off |
| disclosure triangle | don't use | expander arrow |
| display (verb) | transitive only | appears, is displayed |
| document / documentation | "this document" not article, page, topic; spell out documentation | - |
| documentation set | spell out docset | documentation set |
| does not yet | avoid | drop |
| dojo | don't use | training, workshop |
| downscope | avoid; define | constrain scope, reduce scope |
| drag | one verb for the whole gesture; drag-and-drop only as an adjective | drag |
| drag-and-drop | ok as adjective | - |
| drop-down | omit when possible; not standalone noun | list, menu |
| dumb down | don't use | simplify |
| dummy | never use for a placeholder | placeholder |
| dummy variable | don't use | placeholder |
| e.g. | don't use | for example, such as |
| each | individual items, not all | - |
| earlier | for version ranges; not lower | - |
| easy, easily | avoid | drop |
| ecommerce | one word | - |
| egress | lowercase networking | - |
| either | parallel structure; two options only | - |
| elderly, seniors | avoid | older adults |
| element (HTML) | a tag is only the opening or closing part | element |
| email | one word; not a verb | send email |
| emoji | same singular and plural | - |
| enable | consistent with turn on; lets you for feasibility | - |
| endpoint | one word | - |
| enter | text entry | type only when keying matters |
| error-prone | hyphen | - |
| etc. | avoid; with period always. If the list is partial, say so in its introduction | such as, including |
| eventually | avoid | drop |
| execute | prefer simpler | run |
| existing | usually adds nothing; drop (use pre-existing only when contrast matters) | drop |
| expander arrow | the arrow that expands a section; zippy and expando are slang | expander arrow |
| exploit | only negative sense | use |
| extract | use | unzip, untar, unarchive, uncompress |
| fail over (verb) | two words verb; failover noun | - |
| falls back to | skill row: figurative phrasal verb | uses X instead |
| fat | don't use | high-capacity, full-featured |
| female adapter | don't use | socket |
| FHIR | "a FHIR" | - |
| figure out | skill row: phrasal verb | determine, find |
| file name | one word | filename |
| file system | two words | - |
| filename | one word | - |
| fill in | individual fields | - |
| fill out | whole form | - |
| final solution | don't use | solution |
| find out | skill row: phrasal verb | learn, check |
| fintech | expand once; lowercase | financial technology (fintech) |
| first-class | don't use | specific property |
| first-class citizen | figurative | fully supported |
| following | as a noun phrase it's fine; add a noun when it helps clarity or accessibility | - |
| foo | avoid | meaningful placeholder |
| for example | comma after; set off the example | - |
| for instance | don't use | for example |
| from now on | skill row: timeless wording; drop (release notes may say now) | drop |
| frontend | one word | - |
| functionality | use with caution | features, capabilities |
| future | avoid | drop |
| gender-neutral he | don't use | they |
| generative AI | spell out; sentence case; no gen AI | - |
| gets to work | skill row: idiom | starts, runs |
| ghetto | don't use | clumsy, workaround |
| gimp | don't use | specific deficiency |
| grandfathered | don't use | legacy, exempt |
| gray-box | avoid | translucent-box testing |
| grayed-out | don't use | unavailable |
| graylist | don't use | provisional list |
| guru | avoid | expert, teacher |
| guys | don't use | everyone, folks |
| gypsy | don't use | Romani, Roma |
| hamburger menu | don't use | aria-label of icon |
| hands-off | avoid | automated |
| hands-on | avoid | customizable, describe it |
| hang, hung | don't use for unresponsive | stop responding |
| hardcode | no hyphen | - |
| he, him, his | only for known individual | they |
| health check | use with caution | responsive |
| healthcare | one word | - |
| healthy | don't use | responsive |
| high availability | noun open; adjective hyphen | - |
| higher (version) | don't use | later |
| hit (key) | don't use | press, click, enter |
| hit the ground running | skill row: idiom | start quickly, or drop |
| hold the pointer over | when waiting for UI matters | point to |
| holiday | don't use for year end | specific month |
| hostname | one word | - |
| hot (failover) | avoid jargon or define | - |
| hotspot | noun only; define | - |
| housekeeping | don't use | maintenance, cleanup |
| hover | don't use | hold the pointer over, point to |
| HTTPS | caps S | - |
| i.e. | don't use | that is |
| I/O | slash | - |
| ID | caps; not Id | - |
| if ... then | keep then | - |
| image | add context | disk image, container image |
| impact (verb) | don't use | affect |
| in order to | avoid unless clarity | to |
| in the future | timeless wording; drop, or give a version or date | drop |
| index | plural indexes | - |
| ingest | only if heavy processing | import, load, copy |
| ingress | lowercase networking | - |
| inline | one word | - |
| interface (verb) | don't use | interact, communicate |
| internet | lowercase | - |
| IoT | lowercase o | - |
| IPsec | lowercase sec | - |
| just | avoid | drop, only |
| k8s | don't use | Kubernetes |
| Kbps | use Kbps not Kb/s | - |
| kebab case | don't use | dash-case |
| kebab menu | don't use | aria-label |
| key (adjective) | don't use | important |
| key pair | public/private pair | - |
| key-value pair | hyphen | - |
| kill | avoid | stop, exit, cancel, end |
| kill switch | skill row: figurative | emergency stop, off setting |
| lame | don't use | specific deficiency |
| later | for version ranges | - |
| latest | avoid unless anchored by version or date | - |
| learnings | don't use | knowledge, what you learned |
| left-nav | don't use directional | navigation menu |
| legacy | define if used; not pejorative | - |
| let's | avoid | - |
| leverage | avoid | use, build on, take advantage of |
| lifecycle | one word | - |
| like | ok for comparison or examples | - |
| limits | specify kind | usage limit, service limit |
| lint | lowercase | - |
| little-endian | hyphen, lowercase | - |
| livestream | one word | - |
| load balancing | noun open; adjective hyphen | - |
| log in | follow the product UI if it says so; otherwise use sign in as the verb | sign in |
| login (noun) | noun is sign-in; verb is sign in | sign-in, sign in |
| long-running operation | hyphen | - |
| look at | skill row: phrasal verb | read, inspect |
| low-hanging fruit | skill row: idiom | easy wins stated plainly, or a specific list |
| lower (version) | don't use | earlier |
| make use of | skill row: phrasal verb | use |
| male adapter | don't use | plug |
| man hours | avoid | person hours |
| man-in-the-middle | avoid | on-path attacker, person-in-the-middle |
| manmade | avoid | artificial, synthetic |
| manned | avoid | staffed |
| manpower | avoid | staff, workforce |
| Markdown | capital M | - |
| master | avoid; never with slave | primary, main, controller |
| matrix | plural matrixes | - |
| may | keep for formal permission only | can, might |
| media type | the current name for a content type value | media type |
| meta* | closed compounds | - |
| method | avoid generic use in programming docs | - |
| microservices | lowercase one word | - |
| might | possibility | - |
| MIME type | don't use | media type |
| mobile (noun) | don't use | mobile phone, mobile device |
| mom test | don't use | beginner user test |
| monkey test | don't use | automated random test |
| multi-cluster | hyphen exception | - |
| must | requirement | - |
| N/A | write with the slash; spell out on first use | not applicable |
| name server | two words | - |
| namespace | one word | - |
| native | avoid | built-in |
| native speaker | don't split readers this way | readers who use English as another language, or drop |
| navigation bar | don't use for menu | navigation menu |
| neither | neither nor | - |
| new, newer | avoid in timeless text; if you must use it, give a version or release date. Keep it where the source contrasts new with existing | drop, give version |
| ninja | don't use for person | expert |
| non* | no default: the guide leaves it to judgment, readability, and consistency (noninteractive, non-integer). Where the source or the document has an established form, keep it (non-printing). Otherwise the rows below decide. The checker reports a hyphen in the four closed words only at `--info` | - |
| non-interactive | the guide writes it closed; keep the hyphen where the document consistently uses it | noninteractive |
| nonce | define; use cautiously | - |
| normal | skill row: avoid when it means people or ability; ok for default behavior | typical, default |
| NoSQL | one word | - |
| now | avoid: the word is implied. Keep it when the text compares past and present, such as a limit that changed between two named versions | drop |
| nuke | don't use | remove |
| OAuth 2.0 | this spelling | - |
| off-the-shelf | avoid | ready-made, prebuilt |
| old, older | don't use | earlier |
| omnibox | don't use | address bar |
| on-premises | hyphen always; never on-premise | - |
| once (after) | don't use | after |
| out of the box | idiom | by default |
| outside the box | avoid figurative | - |
| page | use for a web page; this document, not this page, when naming the text you are writing | - |
| parameter | usually query parameter | - |
| parent-child | hyphen | - |
| per | rates only | each, for each |
| performant | avoid | precise term |
| persist (transitive) | don't use | persistent |
| personally identifiable information | PII | - |
| pets versus cattle | don't use | persistent versus dynamic |
| plain text | plaintext only in crypto | - |
| please | avoid except apology or favor | - |
| plugin | noun; plug-in adjective; plug in verb | - |
| point to | mouse pointing | - |
| POJO | only for Java audience | simple object |
| pop-up | don't use | dialog, menu |
| populate | processes only; people fill in | - |
| port | listen on | - |
| possible | don't use for can | you can |
| postmortem | avoid | retrospective |
| practitioner | define roles | - |
| pre* | closed except pre-existing, pre-shared | - |
| prebuilt | one word | - |
| preferred pronouns | don't use | pronouns |
| presently | avoid | drop |
| press | keys and mechanical buttons | - |
| primitive | never disparaging | - |
| proper, properly | avoid | technical detail |
| pros | don't use | advantages |
| pulls in | skill row: figurative phrasal verb | installs, downloads, includes |
| quick, quickly | avoid | drop |
| quota | prefer usage limit unless standard term | - |
| RDP (verb) | don't use | connect using RDP |
| read-only | hyphen | - |
| redline (verb) | don't use | track changes |
| regex | don't use | regular expression |
| repo | don't use | repository |
| Representational State Transfer | don't expand | REST |
| retarded | don't use | slowed |
| retriable | don't use | can be tried again |
| review | read vs critique | read |
| RFC | space before number | - |
| roll out | define or avoid | gradual, in stages |
| RTFM | don't use | see |
| runbook | one word | - |
| runtime | noun environment; run time = during execution | - |
| sane | don't use | valid |
| sanity | don't use for checks or values | valid, quick check |
| sanity check | don't use | quick check, coherence check |
| SAP | "an SAP" | - |
| scale | add direction or magnitude | - |
| screenshot | noun only | take a screenshot |
| scroll | prefer go to; no directions | - |
| select | choose, mark checkbox | - |
| sensitive | data harmful if released | - |
| service level agreement | lowercase generic | - |
| set off | skill row: phrasal verb | trigger |
| setup | noun, adjective; verb set up | - |
| sexy | don't use | fast, powerful |
| SHA-1 | hyphen | - |
| shall | avoid | - |
| she, her | only known individual | they |
| sherpa | avoid | guide |
| shift left | avoid | shift earlier |
| should | avoid; use must for requirements, can for options, might for possibilities, and plain present tense for expected results | must, can, might, or a plain verb |
| sign in | verb is sign in, noun is sign-in; write sign in to, never sign into | sign in |
| sign into | don't use | sign in to |
| sign out | verb; sign-out noun | - |
| sign-on | only inside single sign-on | - |
| silver bullet | skill row: idiom | single fix |
| simple, simply | avoid | drop |
| since (reason) | don't use | because |
| single most | two words | - |
| single pane of glass | avoid | single interface |
| slave | don't use | worker, replica |
| slice and dice | don't use | segment data |
| smartphone | don't use | mobile phone |
| soon | avoid; if the source gives a date or version, write that | drop |
| spin up | avoid | create, start |
| SQL | "a SQL" | - |
| ssh | not a verb | connect by using SSH |
| startup | noun; start up verb | - |
| STONITH | avoid | fence failed nodes |
| subcommand | sub-command spelled | - |
| subtree | one word | - |
| such as | introduces examples; no etc. | - |
| surface (verb) | avoid | expose, make available |
| swim lane | jargon | lane, track, or a plain description |
| tab | refer to a tab as "the NAME tab"; use on, not in | - |
| tag | names only the opening or closing part of an element | element |
| tarball | don't use | tar file |
| target (verb) | avoid | intended for |
| text box | don't use | box |
| that | keep in relative clauses; don't drop it | - |
| then | add after an "if" clause, especially a long or complex one; this skill lets a short imperative skip it | if X, then Y |
| they (singular) | preferred; plural verb | - |
| third party | noun; third-party adjective | - |
| this page | refers to the text you are writing | this document |
| this, that | usually add a noun; skip it only when the prose turns clunky, and know what the noun is | - |
| time to live | no hyphens; TTL | - |
| time zone | noun; time-zone adjective. Spell out the region and add the UTC offset; no abbreviation; keep the city the source names | - |
| timeframe | avoid | period, schedule |
| timeout | noun; time out verb | - |
| timestamp | one word | - |
| tl;dr | don't use | To summarize |
| toolkit | one word | - |
| trade-off | closed compound | tradeoff |
| traditional | avoid | conventional, specific |
| transpile | short form only | transpile |
| tribal knowledge | don't use | group knowledge |
| trojan | lowercase | - |
| turn on | consistent with enable | - |
| type (keys) | use enter for text; type only when the keystrokes themselves matter | enter |
| typically | don't open a sentence with it | drop it, or move it inside |
| UI | don't use generically | page, console, web interface |
| unarchive | don't use | extract |
| uncheck | don't use | clear |
| uncompress | don't use | extract |
| under (UI) | don't use | in the field, for |
| under the hood | idiom | internally |
| Unicode | capital U only | Unicode |
| Unix epoch time | the exact name for seconds since 1970 | Unix epoch time |
| Unix-like | hyphen | - |
| unselect | don't use | clear, deselect |
| untar | don't use | extract |
| unzip | don't use | extract |
| US | no periods | US |
| user | only for end users of software reader builds | you |
| user base | two words | - |
| using | use by using or that use if ambiguous | - |
| UTF | hyphen: UTF-8 | - |
| utilize | don't use for use | use |
| v (version) | lowercase | - |
| via | don't use | through, by |
| vice versa | don't use | explicit relationship, conversely |
| voila | don't use | - |
| voodoo | don't use | mysterious, nondeterministic |
| vs. | don't use | versus |
| walkthrough | one word | - |
| war room | don't use | response team |
| warm (failover) | avoid jargon or define | - |
| we | avoid for reader tasks; ok when the authoring organization acts | you |
| web | lowercase | - |
| web server | two words | - |
| WebAssembly, Wasm | follow spec | - |
| webmaster | don't use | website owner |
| while (contrast) | don't use | although |
| white glove | avoid | high-touch, premium |
| white label | don't use | unbranded |
| white-box | avoid | clear-box testing |
| whitehat | don't use | legal, ethical |
| whitelist | don't use | allowlist, safelist |
| whitepaper | one word; be specific | - |
| whitespace | one word | - |
| wildcard | one word | - |
| will | avoid for present behavior; keep only for a real later event | present tense |
| wish | don't use | want, need |
| with (ownership/use) | don't use | has, use |
| workload | define | - |
| World Wide Web | don't use | web |
| would | avoid | can |
| ymmv | don't use | Your results might vary |
| you | address reader | - |
| You're ready to go | skill row: upbeat closer with no information | drop, or state the next step |
| zippy | don't use | expander arrow |

<!-- check-style: on -->

Source: adapted and condensed from the Google developer documentation style guide word list, https://developers.google.com/style/word-list, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Rewritten in new words, with Google-product, Android-only, and Cloud-only entries left out. Not affiliated with or endorsed by Google.
