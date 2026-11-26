# Links, cross-references, and UI instructions

Rules for link text, link introductions, heading anchors, references to other parts of a document, and instructions that name UI elements and keys.

## Contents

- [Choosing links](#choosing-links)
- [Link text](#link-text)
- [Introducing a link](#introducing-a-link)
- [Unexpected link behavior](#unexpected-link-behavior)
- [Links to code elements](#links-to-code-elements)
- [Heading anchors](#heading-anchors)
- [Referring to the document itself](#referring-to-the-document-itself)
- [Focus and format of UI instructions](#focus-and-format-of-ui-instructions)
- [UI terms and prepositions](#ui-terms-and-prepositions)
- [UI verbs](#ui-verbs)
- [Menu paths](#menu-paths)
- [Keyboard keys](#keyboard-keys)
- [Keep the source's facts](#keep-the-sources-facts)

## Choosing links

- Link selectively. Every link risks losing the reader.
- When one or two sentences give the reader what they need, write them inline instead of linking.
  - wrong: `Run the server (see [What is a server?](/glossary#server)).` -> right: `Run the server, the process that answers requests.`
- Link third-party standards and products instead of re-documenting them.
- In general, link a destination once per page, where it helps most. A second link is fine for a deep link to a section, a distant repeat in a very long page, or another entry point.
  - wrong: three links to the same page in three adjacent paragraphs -> right: one link, at first mention
- Point to the single best page and the best heading on it. Don't add a second link for the same purpose.

## Link text

- Make the link text name the destination. Use the exact title of the target, or a short descriptive phrase with the important words first.
  - wrong: `For setup steps, click [here](/setup).` -> right: `For setup steps, see [Set up authentication](/setup).`

<!-- check-style: off -->

- Don't use "this document", "this page", "link", or "click here" as link text.

<!-- check-style: on -->

  - wrong: `See [this guide](/guide).` -> right: `See [Deploy to staging](/guide).`
- Make the link text a title that names the destination, not the bare address. Legal documents such as terms of service are the exception.
  - wrong: `See [https://example.com/docs/auth](https://example.com/docs/auth).` -> right: `See [Authentication overview](https://example.com/docs/auth).`
- Two links in one document that read the same must go to the same place.
- Leave quotation marks and end punctuation outside the link.
  - wrong: `see ["Run the tests."](/tests)` -> right: `see [Run the tests](/tests).`
- When a name is followed by its abbreviation in parentheses, link both as one unit.
  - wrong: `[Message Queue](/mq) (MQ)` -> right: `[Message Queue (MQ)](/mq)`
- An unlinked reference to a section uses quotation marks, and an unlinked book or film title uses italics.

## Introducing a link

- Introduce a stand-alone cross-reference with `For more information, see` or `For more information about X, see`.
  - wrong: `Learn more at [Manage quotas](/quotas).` -> right: `For more information, see [Manage quotas](/quotas).`
- If the link text alone doesn't tell readers why to follow it, say what it's about.
  - wrong: `For more information, see [Reference](/ref).` -> right: `For more information about retry limits, see [Reference](/ref).`
- Use "about", never "on", in that phrase.
  - wrong: `For more information on quotas, see [Usage limits](/limits).` -> right: `For more information about quotas, see [Usage limits](/limits).`
- Use "see" to point at a link or cross-reference.
  - wrong: `Refer to [Install the CLI](/install).` -> right: `For more information, see [Install the CLI](/install).`
- Say "read" when readers meet text for the first time. "Review" implies a critical check.
  - wrong: `Review the install guide before you begin.` -> right: `Read the install guide before you begin.`

## Unexpected link behavior

- If a link triggers a download, say so and give the format.
  - wrong: `Get the [audit log](/audit.csv).` -> right: `Download the [audit log (CSV)](/audit.csv).`
- Say so when a link opens an email, jumps to a section of the same page, or opens in a new tab.
  - wrong: `[Contact us](mailto:help@example.com)` -> right: `[Email the support team](mailto:help@example.com)`
  - wrong: `See [Limits](#limits).` -> right: `For more information, see the [Limits](#limits) section of this document.`
- Don't force a new tab. If it's unavoidable, add "(opens in a new tab)" to the link text.
- Don't rely on an external-link icon. When it matters that the reader leaves your site, say it in the sentence.
  - wrong: a link to [virtual environments](https://docs.python.org/3/tutorial/venv.html) that only an icon marks as external -> right: `For more information, see the Python tutorial about [virtual environments](https://docs.python.org/3/tutorial/venv.html).`
- Avoid linking outside the documentation set from its sidebar or table of contents. If you must, make clear that the destination is another site.
- A link to a section of another page reads like any other cross-reference. If your page already has a heading with that name, say which document the section is in.

## Links to code elements

- When the link text includes a command or flag, put it in code font and add its description to the link text. Skip the description if it's awkward or redundant.
  - wrong: ``Run the command with the [`--timeout`](/ref#timeout) flag.`` -> right: ``Run the command with the [`--timeout` flag](/ref#timeout).``
- For a list of short related items, link each name and skip the repeated noun.
  - wrong: ``The cache supports the [`get` command](/get), [`set` command](/set), and [`delete` command](/delete).`` -> right: ``The cache supports the [`get`](/get), [`set`](/set), and [`delete`](/delete) commands.``

## Heading anchors

- When other pages link to a heading, give it an explicit anchor: lowercase words joined by hyphens, short but descriptive.
  - wrong: `## Set up auth {: #Set_Up_Auth }` -> right: `## Set up auth {: #set-up-auth }`
- When you rename a heading that is linked to, keep its old anchor on the renamed heading.
  - wrong: rename `## Install` to `## Install the CLI` and let `#install` break -> right: `## Install the CLI {: #install }`
- Change an existing custom anchor only when its wording is the problem, and then update every link to it.
- The `{: #id }` form needs a renderer that supports attribute lists. This skill adds a fallback for plain GitHub-flavored Markdown: put `<a id="set-up-auth"></a>` before the heading, or keep the heading text stable.

## Referring to the document itself

- To refer to the text you're writing, say "this document". Write "documentation" in full. The word list holds the rejected alternatives.
  - wrong: `This page shows how to set up a proxy.` -> right: `This document shows how to set up a proxy.`
  - This skill's own preference, not Google's: begin with the task instead, as in `To set up a proxy, follow these steps:`
- Don't point at position. Use "preceding" and "following", or restructure.
  - wrong: `the settings shown above` -> right: `the preceding settings`
  - wrong: `The example below uses a proxy.` -> right: `The following example uses a proxy.`
- When "following" has no noun, add one if the sentence is unclear or if accessibility tools read it alone.
  - wrong: `Use the following.` -> right: `Use the following command.`
- Define an ambiguous noun the first time you use it: image (disk or container), key (which kind), method (class member or approach), limit (which limit).

## Focus and format of UI instructions

- Describe the goal, not the widget, when the action is clear. Give UI detail only when the UI is the subject or the gesture is unclear.
  - wrong: `Click the reload icon in the browser toolbar.` -> right: `Reload the page.`
  - If the source names a control or a menu path, keep the name even when the goal is clear. See [Keep the source's facts](#keep-the-sources-facts).
- Bold the exact label of a button, menu, dialog, window, or list item. Don't quote it, and don't add the element type after a button label.
  - wrong: `Click the "Save" button.` -> right: `Click **Save**.`
- Copy the capitalization from the screen. When a label shows in all capitals, or several labels are cased inconsistently, write sentence case.
  - wrong: `Click **SAVE**.` -> right: `Click **Save**.`
- Drop a trailing ellipsis from a label.
  - wrong: `Click **Choose file...**.` -> right: `Click **Choose file**.`
- Don't use a UI label as a verb or a noun.
  - wrong: `**Delete** the record.` -> right: `To remove the record, click **Delete**.`
  - wrong: `**Label** the volume.` -> right: `In the **Label** box, enter a name for the volume.`

<!-- check-style: off -->

- Don't use position or direction words for an element: above, below, left, right-hand, top-right.

<!-- check-style: on -->

  - wrong: `Click the icon in the top-right corner.` -> right: `On the toolbar, click ⚙ **Settings**.`
  - The symbol before the label stands for the button's icon. For an item that's hard to find, give the tooltip name, the section name, or a screenshot with alt text.
- If the source tells the reader where a control is, keep that information and name the container instead of the direction.
  - wrong: `In the left pane, select **Providers**.` -> right: `In the list of sections, select **Providers**.`
- Name an icon button by its tooltip text and put the icon before the name.

## UI terms and prepositions

- Name controls by label plus type: the **Name** tab, the **Owner** box, the **Terms** checkbox. Use "the **NAME** list" for a list box. Documentation for Google Cloud or Google Workspace says "field" instead of "box". Keep one of the two terms per document.
  - wrong: `In the Hostname text box ...` -> right: `In the **Hostname** box ...`
- Use "in" for dialogs, fields, lists, menus, panes, and windows. Use "on" for pages, tabs, and toolbars.
  - wrong: `On the Settings dialog ...` -> right: `In the **Settings** dialog ...`
  - wrong: `In the Create page ...` -> right: `On the **Create** page ...`

<!-- check-style: off -->

- Use "dialog" (not pop-up), "page" for a web page, "pane" or "panel", and "section".
- Use "menu" (not drop-down), "navigation menu" (not navigation bar), "address bar" (not omnibox), and "expander arrow" (not zippy). Write "checkbox" as one word.
  - wrong: `In the pop-up, open the drop-down.` -> right: `In the dialog, open the menu.`
- Don't use "UI" as a catch-all. Name the page or the web interface.
- Don't name hamburger or kebab menus that way. Use the icon's label.
- Say "select" and "clear" for checkboxes, not "check", "uncheck", or "deselect".
  - wrong: `Uncheck the box.` -> right: `Clear the checkbox.`
- Don't use "toggle" as a verb. Say "turn on" or "turn off", and keep one of "enable" or "turn on" for the whole document.
  - wrong: `Toggle the switch.` -> right: `Turn on the switch.`
- "Fill in" is for a field, and "fill out" is for a whole form. Don't tell the reader to "copy and paste". Say what to enter.

<!-- check-style: on -->

  - wrong: `Copy the token and paste it into the field.` -> right: `Enter the token in the **Token** field.`
- Avoid "scroll". Say "go to the section".

## UI verbs

- Use these verbs in steps: click, choose, drag, enter, go to, hold the pointer over, press, select, turn on, turn off.
- Click a mouse target without "on".
  - wrong: `Click on OK.` -> right: `Click **OK**.`
- Press a key. Enter text, and use "type" only when the keystrokes matter.
  - wrong: `Type your password and hit Enter.` -> right: `Enter your password, and then press Enter.`

<!-- check-style: off -->

- Don't write "hover" or "navigate to". Use "point to" or "hold the pointer over", and "go to".

<!-- check-style: on -->

  - wrong: `Hover over the menu, then navigate to Tools.` -> right: `Point to the menu, and then go to **Tools**.`
- Use "choose" for a general pick, and "select" for an item or option in the UI.
- Drag is one verb. Don't write "click and drag" or "drag and drop" as a verb.

## Menu paths

- Write a menu path as one bold span with `>` between items. Use it only for menu items.
  - wrong: `**Run** -> **Debug** -> **Attach to process**` -> right: `**Run > Debug > Attach to process**`
- In rendered HTML, put a nonbreaking space before each `>`. Add an `aria-label` of "and then" to each `>`, so that screen readers don't say "greater than".
- For mixed element types, write the steps in separate sentences.
  - wrong: `**File > Export > the Format list > PDF**` -> right: `Select **File > Export**. In the **Format** list, select **PDF**.`

## Keyboard keys

- Spell out modifier keys: Control, Command, Option, Shift. Don't use symbols or abbreviations.
  - wrong: `To open the log pane, press Ctrl-Shift-L or ⌘⇧L.` -> right: `To open the log pane, press Control+Shift+L (or Command+Shift+L on macOS).`
- Write letter keys in capitals and join keys with a plus sign. Put Shift after another modifier: `Control+Shift+P`.
  - wrong: `Press ctrl+shift+p` -> right: `Press Control+Shift+P`
- Spell out a key that is hard to read in text: comma, hyphen, period, plus.
  - wrong: `Press Control+,` -> right: `Press Control+comma.`
- Give each operating system when they differ. Show the Windows and Linux shortcut first, with the macOS one after it in parentheses.
- If the source names the systems that a shortcut applies to, keep the names.
  - wrong: `Press Control+comma (or Command+comma on macOS).` when the source says the shortcut works on Linux and Windows -> right: `Press Control+comma on Linux and Windows (or Command+comma on macOS).`
- Use code font, not `kbd`, for a shortcut the reader types into a text field.

## Keep the source's facts

This section is this skill's own, not Google's. The rules in this file change how you point at a control, a key, or a link. They don't let you drop what the source says. Keep the fact and reword around the rule:

- The location of a control: name the container, such as a pane, a list, a section, a toolbar, or a tab. If the source gives only a direction, name the container it stands for. Then tell the author what you changed.
  - wrong: `Select **Providers**.` when the source says the sections sit in a left pane -> right: `In the list of sections, select **Providers**.`
- A menu path: keep every item, in order.
  - wrong: `Select **Settings**.` when the source says File, then Settings -> right: `Select **File > Settings**.`
- A list of systems for a shortcut or command: keep the list. See [Keyboard keys](#keyboard-keys).
- An address that the reader must type or compare: keep the address in the link target. Add it in code font after the link text.
  - wrong: the bare address as the link text -> right: ``Open the [status page](https://status.example.com), at `status.example.com`.``

Source: adapted and condensed from the Google developer documentation style guide, https://developers.google.com/style, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Not affiliated with or endorsed by Google.
