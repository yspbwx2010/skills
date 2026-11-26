#!/usr/bin/env python3
"""Report style findings in Markdown documents. Never rewrites files.

Usage:
    check_style.py [--info] [--no-contractions] [--select IDS] [--ignore IDS] PATH...
    check_style.py --self-test
    check_style.py --list-rules

PATH is a Markdown file or a directory (all *.md under it). One finding per
line: path:line:col: rule-id: message. Exit status: 0 clean, 1 findings,
2 usage error. --info adds the info-level checks. --no-contractions skips the
negation-contraction check (use it for reference comments). --select and
--ignore take comma-separated rule ids; "heading" matches every "heading-*".

Prose checks skip fenced and indented code, inline code, link targets, URLs,
HTML tags and comments. Code lines get only the length and placeholder checks.
Terms come from word_list.tsv next to this script.

Known gaps (the script prefers a miss to a false hit):
  * No semantic checks: invented facts, synonym drift, unclear "it", jargon,
    one-instruction-per-step, parallel lists, vague claims. Security overclaim
    is caught as "protects you from", "is safe to" and "prevents" or
    "ensures" in a sentence with a security noun (sandbox, secure, protect).
  * Doc comments inside code fences are not read as prose. Run the checker on
    extracted comment text if you need that.
  * Passive voice, "If" without "then" and repeated openings are info-level
    guesses. "while" and "once" are checked only in the clearest patterns.
  * A list or code block right after a heading is an info-level finding
    (lead-in-heading): the guide lets the heading give the context. The same
    block after a paragraph without a closing colon, or after a fragment, is
    a default-level lead-in finding. A paragraph that ends in a period, then a
    note paragraph (Note:, Caution:, Warning:), then the block is fine.
    "The following" is a valid noun phrase and is never flagged.
  * Semicolons are flagged unless a conjunctive adverb follows or the
    sentence is a series with commas (two of the three cases the guide
    prefers); the first case (two close clauses) can't be told apart.
  * Em dashes with no spaces are fine; en dashes, "--" and spaced em dashes are
    flagged. A hyphen in one of the four nonX words the guide writes closed
    (noncurrent, nonempty, noninteractive, nonpublic) is an info-level finding:
    the guide leaves non- words to judgment, so a document that consistently
    uses the hyphen is fine.
  * "we recommend" is not flagged; other uses of "we" are.
  * Skipping text on purpose: wrap it in <!-- check-style: off --> and
    <!-- check-style: on -->, or start a list item with "wrong:" (the part
    before "->" is skipped). Table rows skip the semicolon check.
  * Title case is detected only when the capitals are unambiguous: capitals
    on later words, "a" or "an" before two capitalized words, or a two-word
    heading that ends in a common title word (Getting Started, Release
    Notes). A product name such as "Install the Windows Subsystem for Linux"
    passes. A first heading at level 2 is accepted (README sections), level
    3+ is flagged.
  * A heading counts as empty when another heading follows it directly, the
    H1 included (the guide says to follow every heading with content). A
    colon inside double quotes or code font is not a heading-colon finding.
  * Reference checks: URL as link text, 24-hour times near a time zone, zone
    abbreviations (KST, PST; UTC and GMT as labels are fine), numeric ISO
    dates in prose, Ctrl and Cmd, "select File, then Settings", "in the
    toolbar", bold on a value (**18 MiB**; a bold run-in label that ends in
    a period is fine). These look at prose only.
  * Release notes may use "now", "new" and single-item lists. Lists under
    Added/Changed/Fixed headings skip the lead-in check, and a document
    with such headings or "release notes"/"changelog" in a heading skips
    the info-level timeless-info check. Product wording wins over the word
    list (for example a UI that says "log in").
  * "this page" is flagged even where the page is a real web page.
  * Placeholder checks cover shell-like and config blocks, not C-like code.
"""
import argparse
import bisect
import os
import re
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
WORD_LIST = os.path.join(HERE, "word_list.tsv")

RULES = {
    "word-list": "term from word_list.tsv (plus access, type, read only)",
    "modal": "should, may, would, could, shall",
    "timeless": "currently, soon, from now on, in the future, ...",
    "position": "above or below for document position",
    "output-intro": "\"You should see\" instead of showing the output",
    "human-verb": "software that refuses or gives up",
    "overclaim": "protects you from / is safe to / prevents or ensures near a security noun",
    "conjunction": "once or since where after or because is meant",
    "contraction": "negation without a contraction (does not, cannot)",
    "semicolon": "semicolon in prose outside the cases the guide allows",
    "exclamation": "exclamation mark in prose",
    "dash": "en dash, double hyphen or spaced em dash in prose",
    "curly-quote": "curly quotes in prose",
    "ellipsis": "ellipsis in prose",
    "number-comma": "4+ digit count without a thousands comma",
    "non-compound": "info: noncurrent, nonempty, noninteractive or nonpublic with a hyphen",
    "sentence-length": "sentence over 25 words",
    "this-noun": "this/these with no noun after it",
    "file-noun": "file name in code font without the noun file",
    "heading-number": "numbered heading",
    "heading-colon": "colon in a heading",
    "heading-case": "title case heading",
    "heading-empty": "heading directly followed by another heading (H1 included)",
    "heading-level": "first heading, skipped level or second H1",
    "heading-bold": "bold line used as a heading",
    "lead-in": "list or code block after a paragraph with no lead-in colon, or after a fragment",
    "lead-in-heading": "info: list or code block directly after a heading",
    "link-text": "raw URL used as link text",
    "time-24h": "24-hour time next to a time zone",
    "time-zone": "time zone abbreviation such as KST or PST",
    "date-numeric": "numeric YYYY-MM-DD date in prose",
    "key-name": "Ctrl or Cmd instead of Control or Command",
    "menu-path": "\"select File, then Settings\" instead of File > Settings",
    "ui-preposition": "\"in the toolbar\" instead of \"on the toolbar\"",
    "bold-value": "bold used on a value that starts with a digit",
    "placeholder": "<angle>, your-/my-, YOUR_ placeholders",
    "code-length": "code line over 80 characters",
    "passive": "info: passive voice candidate",
    "if-then": "info: If clause without then",
    "repeated-opening": "info: 3+ items or sentences with the same opening",
    "timeless-info": "info: now, new, existing, older",
    "while": "info: while used for contrast",
}
INFO_RULES = {"passive", "if-then", "repeated-opening", "timeless-info", "while",
              "lead-in-heading", "non-compound"}

# ---------------------------------------------------------------- word list

TERM_GROUPS = {}
for _t in ("should", "may", "would", "could", "shall"):
    TERM_GROUPS[_t] = "modal"
for _t in ("currently", "presently", "eventually", "soon", "as of this writing",
           "does not yet", "from now on"):
    TERM_GROUPS[_t] = "timeless"
TERM_GROUPS["refuses to"] = "human-verb"
TERM_GROUPS["gives up"] = "human-verb"

# term -> (regex for text before, regex for text after); a match skips the hit
CONTEXT_SKIP = {
    "soon": (r"\bas\s+$", None),
    "may": (None, r"^\s+\d"),
    "desired": (None, r"^\s+state\b"),
    "quick": (None, r"^\s+start"),
    "simple": (r"\b(?:Simple|SIMPLE)\s+$", None),
    "just": (None, r"^\s+in\s+time\b"),
    "we": (None, r"^\s+recommend"),
}


def load_word_list(path=WORD_LIST):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            cells = line.split("\t") + ["", ""]
            variants = [v.strip() for v in cells[0].split("|") if v.strip()]
            if variants:
                rows.append((variants, cells[1].strip(), cells[2].strip()))
    return rows


def build_matcher(rows):
    lookup, alts = {}, []
    for variants, guidance, repl in rows:
        for v in variants:
            lookup[" ".join(v.lower().split())] = (variants[0], guidance, repl)
            alts.append(v)
    alts.sort(key=len, reverse=True)
    body = "|".join(r"\s+".join(re.escape(w) for w in v.split()) for v in alts)
    rx = re.compile(r"(?<![\w/@#$.-])(?:" + body + r")(?![\w@-]|[./:]\w)", re.I)
    return rx, lookup


# ---------------------------------------------------------------- patterns

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`]*)")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
LIST = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])([ \t]+)(\S.*)$")
NOTICE = re.compile(r"\W*(?:Note|Caution|Warning|Tip|Important)\b")
HR = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
IMAGE = re.compile(r"!\[[^\]\n]*\]\([^)\n]*\)")
LINK = re.compile(r"\[([^\]\n]*)\]\(([^)\n]*)\)")
REFLINK = re.compile(r"\[([^\]\n]+)\]\[[^\]\n]*\]")
FOOTNOTE = re.compile(r"\[\^[^\]\n]+\]")
TAG = re.compile(r"</?[A-Za-z][^<>\n]*>|<https?://[^>\s]+>")
URL = re.compile(r"(?:https?://|www\.)[^\s<>)\]]+|[\w.+-]+@[\w-]+\.[\w.-]+")
ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[A-Za-z]+);")
EMPH = re.compile(r"\*+|(?<!\w)_+|_+(?!\w)")
ESCAPE = re.compile(r"\\[\\`*_{}\[\]()#+.!|<>-]")

SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]\x01\x02]*\s+(?=[\"'(\[\x01\x02]*[A-Z0-9])")

NEGATIONS = {
    "does not": "doesn't", "do not": "don't", "did not": "didn't",
    "is not": "isn't", "are not": "aren't", "was not": "wasn't",
    "were not": "weren't", "has not": "hasn't", "have not": "haven't",
    "had not": "hadn't", "cannot": "can't", "can not": "can't",
    "will not": "won't", "would not": "wouldn't", "should not": "shouldn't",
    "could not": "couldn't",
}
NEG_RX = re.compile(r"(?<![\w-])(" + "|".join(
    sorted((re.escape(k).replace(r"\ ", r"\s+") for k in NEGATIONS), key=len, reverse=True))
    + r")(?!\w)(?!\s+(?:only|just|yet)\b)", re.I)

POSITION = re.compile(
    r"(?<!\w)(above|below)(?!\w)(?=\s*(?:[.,;:)!?]|$)|\s+(?:is|are|shows?|lists?|uses?|"
    r"describes?|contains?|explains?|demonstrates?|illustrates?|gives?)\b)"
    r"|\b(?:the|as|listed|shown|described|mentioned|noted|see)\s+(above|below)\b(?!\s+(?:the|a|an|\d))",
    re.I)
ACCESS = re.compile(
    r"(?<![\w-])access(?:es|ed|ing)?(?=\s+(?:the|your|any|all|a|an|each|every|these|those|its|"
    r"their|other|\x01))", re.I)
TYPE_VERB = re.compile(
    r"(?:(?<![\w`])Type|\b(?:to|you|then|and|can|must|first|also)\s+type)\s+(?=\x01)")
READ_ONLY = re.compile(
    r"\bread only(?=\s+(?:file|files|mode|access|flag|memory|filesystem|file system|volume|"
    r"permission|permissions|bit)\b)|\bread only(?=\s*(?:[.,;:)]|$))", re.I)
OVERCLAIM = re.compile(r"\bprotects?\s+you\s+from\b|\b(?:is|are)\s+safe\s+to\b", re.I)
SECURE_VERB = re.compile(r"(?<![\w-])(prevent|prevents|ensure|ensures)(?![\w-])", re.I)
SECURITY_NOUN = re.compile(
    r"(?<![\w-])(?:sandbox\w*|secur\w*|protect\w*|attack\w*|malicious|threats?|"
    r"vulnerabilit\w+|exploit\w*|unauthori[sz]ed|isolat\w+)(?![\w-])", re.I)
LINK_URL_TEXT = re.compile(r"\[https?://[^\]\s]*\]\(")
TIME_24H = re.compile(
    r"(?<![\d:.])(?:[01]\d|2[0-3]):[0-5]\d(?![\d:])(?!\s*(?:[ap]\.?m\b))", re.I)
ZONE_ABBR = re.compile(
    r"(?<![\w-])(?:KST|JST|PST|PDT|EST|EDT|CST|CDT|CET|CEST|MST|MDT|BST|AEST|AEDT|HST|AKST|"
    r"AKDT|EET|WET)(?![\w-])")
ZONE_NEAR = re.compile(r"(?<![\w-])(?:UTC|GMT)(?![\w-])|Standard Time|time zone")
ISO_DATE = re.compile(
    r"(?<![\w.:/-])\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])(?![\w-])")
KEY_NAME = re.compile(r"(?<![\w-])(Ctrl|Cmd)(?![\w-])")
MENU_THEN = re.compile(
    r"(?<![\w-])(?:[Ss]elect|[Cc]lick|[Cc]hoose)\s+\x02*[A-Z][\w-]*\x02*,\s+(?:and\s+)?then\s+\x02*[A-Z]")
IN_TOOLBAR = re.compile(r"(?<![\w-])in\s+the\s+(?:[\w-]+\s+){0,3}toolbar(?![\w-])", re.I)
BOLD_VALUE = re.compile(r"\*\*(?=\d)(?![^*\n]*\.\*\*)")  # a run-in label ending in a period is fine
OUTPUT_INTRO = re.compile(r"\byou(?:\s+should|\s+will|'ll)\s+(?:see|get)\b", re.I)
ONCE = re.compile(
    r"(?<![\w-])once\s+(?:(?:you|your|it|they|we|the|this|these|those|its|their|all|each|any)\b|"
    r"(?:installed|finished|done|complete|completed|available|ready|configured)\b|"
    r"\S+\s+(?:is|are|has|have|was|were|finishes|completes|starts|ends|exits)\b)", re.I)
SINCE = re.compile(
    r"(?<![\w-])since\s+(?:(?:the|this|that|your|its|their)\s+\S+|it|you|they|we|there)\s+"
    r"(?:is|are|can|cannot|can't|does|doesn't|do|don't|has|have|must|needs?|supports?|lacks?|"
    r"provides?|requires?)\b", re.I)
WHILE = re.compile(r"(?:(?<=[.!?]\s)|^)While\b|,\s+while\b")
SEMICOLON = re.compile(r"(?<!tl);")
CONJ_ADVERB = re.compile(
    r"\s*(?:therefore|however|moreover|furthermore|consequently|thus|otherwise|instead|"
    r"that is|for example|for instance|in addition|in other words)\b", re.I)
EXCLAMATION = re.compile(r"!(?=\s|$)")
DASH = re.compile(r"–|(?<=\s)--(?=\s)|(?<=\s)—|—(?=\s)")
CURLY = re.compile("[‘’“”]")
ELLIPSIS = re.compile("…|\\.\\.\\.")
NUMBER = re.compile(
    r"(?<![\w.,:/#$@+-])\d{4,}(?=\s+(?:bytes?|bits?|[KMGT]i?B|files?|lines?|characters?|chars?|"
    r"tokens?|requests?|seconds?|milliseconds?|ms|items?|users?|rows?|entries|words?|times|"
    r"records?|messages?|connections?|errors?|calls?|queries|events?)\b)")
NON_COMPOUND = re.compile(r"(?<![\w-])non-((?:current|empty|interactive|public)(?![\w-]))")
THIS = re.compile(
    r"(?<![\w-])(?<!like )(?<!all )(this|these)(?=\s*(?:[.,;:)!?]|$)|\s+(?:is|are|was|were|will|"
    r"can|could|may|might|should|must|does|do|did|has|have|means|helps|allows|lets|makes|causes|"
    r"usually|also|only|often|always|never|happens|occurs|works|ensures|prevents|enables|keeps|"
    r"gives|shows|returns|uses|requires|needs|to|in|for|with|by|on|at)\b)", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?"
    r"(?!(?:based|related|limited|supposed|designed|used\s+to)\b)"
    r"(?:\w{3,}ed|built|made|given|shown|run|set|used|written|read|sent|kept|found|known|"
    r"taken|done|chosen|stored|left|held|seen|put)\b", re.I)
TIMELESS_INFO = re.compile(r"(?<![\w-])(now|new|newer|existing|older)(?![\w-])", re.I)
FILE_LIKE = re.compile(
    r"^(?:[~.\w/\\-]+/)?[\w.-]+\.(?:toml|json|ya?ml|md|py|txt|cfg|ini|conf|js|ts|sh|rs|cpp|hpp|"
    r"h|cmake|xml|html|css|lock|log|env)$")
ANGLE = re.compile(r"(?<![\w<>-])<[A-Za-z][\w .-]*>")
POSSESSIVE = re.compile(r"(?<![\w-])(?:your|my)[-_][A-Za-z0-9_-]+", re.I)
HTML_TAGS = {"a", "b", "br", "code", "div", "em", "h1", "h2", "h3", "hr", "i", "img", "li",
             "ol", "p", "pre", "span", "strong", "table", "td", "th", "tr", "ul", "var"}
FRAG_END = {"to", "in", "with", "by", "as", "on", "for", "run", "are", "is", "of", "at",
            "from", "and", "or", "using"}
LOWER_ARTICLES = {"a", "an"}
TITLE_WORDS = {"started", "start", "settings", "options", "overview", "introduction", "usage",
               "setup", "installation", "configuration", "reference", "guide", "notes", "limits",
               "steps", "basics", "issues", "requirements", "commands", "features", "examples",
               "changes", "updates", "concepts", "tutorial", "troubleshooting", "support",
               "details", "summary"}
FUNC_CAPS = {"And", "Or", "The", "A", "An", "To", "For", "Of", "In", "On", "With", "From",
             "By", "At", "As", "Into", "Your", "Is", "Are", "Not", "Up", "Out", "Over", "Via"}
BOLD_LINE = re.compile(r"^(\*\*|__)[^*_].*?\1\s*:?\s*$")
WRONG_ITEM = re.compile(r"\s*wrong\b[^:\n]*:")
CHECK_OFF = re.compile(r"<!--\s*check-style:\s*off\s*-->")
CHECK_ON = re.compile(r"<!--\s*check-style:\s*on\s*-->")
CHANGELOG_HEADINGS = {"added", "changed", "fixed", "removed", "deprecated", "security",
                      "new features", "improvements", "bug fixes", "breaking changes"}
PLACEHOLDER_LANGS = {"", "sh", "bash", "shell", "console", "zsh", "fish", "terminal", "text",
                     "toml", "yaml", "yml", "ini", "powershell", "bat", "cmd", "sh-session"}
NO_LENGTH_LANGS = {"text", "output", "log", "plaintext", "diff"}


# ---------------------------------------------------------------- parsing

def fill(m, ch):
    return re.sub(r"[^\n]", ch, m.group())


def mask(raw):
    """Same-length copy: code is \\x01, link targets, URLs, tags, emphasis are \\x02."""
    s = CODE_SPAN.sub(lambda m: fill(m, "\x01"), raw)
    s = IMAGE.sub(lambda m: fill(m, "\x02"), s)

    def keep_text(m):
        t = m.group(1)
        return "\x02" + t + "\x02" * (len(m.group()) - len(t) - 1)

    s = LINK.sub(keep_text, s)
    s = REFLINK.sub(keep_text, s)
    for rx in (FOOTNOTE, TAG, URL, ENTITY, EMPH, ESCAPE):
        s = rx.sub(lambda m: fill(m, "\x02"), s)
    return s


def skip_regions(lines):
    """Blank the lines between a check-style off marker and the next on marker."""
    out, off = [], False
    for line in lines:
        if CHECK_OFF.search(line):
            off = True
        if off:
            out.append("")
            if CHECK_ON.search(line):
                off = False
        else:
            out.append(line)
    return out


def parse(lines):
    """Split a document into blocks: heading, p, li, quote, table, fence, icode, hr."""
    blocks, cur = [], None
    fence, in_comment, in_list = None, False, False
    start = 0
    if lines and lines[0].strip() == "---":
        for k in range(1, min(len(lines), 60)):
            if lines[k].strip() == "---":
                start = k + 1
                break
    for n in range(start + 1, len(lines) + 1):
        line = lines[n - 1]
        s = line.strip()
        if fence:
            ch, size = fence.marker
            if s.startswith(ch * size) and not s.strip(ch):
                fence = None
            else:
                fence.lines.append((n, line))
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if not s:
            cur = None
            continue
        m = FENCE.match(line)
        if m:
            fence = SimpleNamespace(kind="fence", lang=m.group(3).lower(), lines=[], start=n,
                                    marker=(m.group(2)[0], len(m.group(2))), parts=[])
            blocks.append(fence)
            cur = None
            if not m.group(1):
                in_list = False
            continue
        if s.startswith("<!--"):
            in_comment = "-->" not in s
            continue
        indent = len(line) - len(line.lstrip(" "))
        m = HEADING.match(line)
        if m:
            blocks.append(SimpleNamespace(kind="heading", level=len(m.group(1)),
                                          parts=[(n, m.start(2), m.group(2))]))
            cur, in_list = None, False
            continue
        if HR.match(line):
            blocks.append(SimpleNamespace(kind="hr", parts=[]))
            cur, in_list = None, False
            continue
        m = LIST.match(line)
        if m:
            cur = SimpleNamespace(kind="li", parts=[(n, m.start(4), m.group(4))],
                                  list_start=not in_list)
            blocks.append(cur)
            in_list = True
            continue
        if s.startswith("|"):
            cur = None
            if not TABLE_SEP.match(line):
                blocks.append(SimpleNamespace(kind="table", parts=[(n, 0, line)]))
            continue
        if s.startswith(">"):
            col = line.index(">") + 1
            text = line[col:]
            if text.startswith(" "):
                col, text = col + 1, text[1:]
            if cur is not None and cur.kind == "quote":
                cur.parts.append((n, col, text))
            else:
                cur = SimpleNamespace(kind="quote", parts=[(n, col, text)])
                blocks.append(cur)
            continue
        if indent >= 4 and cur is None and not in_list:
            blocks.append(SimpleNamespace(kind="icode", parts=[]))
            continue
        if cur is not None:
            cur.parts.append((n, indent, line[indent:]))
            continue
        if not (in_list and indent >= 2):
            in_list = False
        cur = SimpleNamespace(kind="p", parts=[(n, indent, line[indent:])], in_list=in_list)
        blocks.append(cur)
    return blocks


# ---------------------------------------------------------------- checker

class Checker:
    def __init__(self, info=False, contractions=True, select=None, ignore=None, words=None):
        self.info, self.contractions = info, contractions
        self.select, self.ignore = select or [], ignore or []
        self.rx, self.lookup = words if words else build_matcher(load_word_list())
        self.found = []
        self.release = False

    def on(self, rule):
        if rule in INFO_RULES and not self.info:
            return False
        if rule == "contraction" and not self.contractions:
            return False

        def hit(ids):
            return any(rule == i or rule.startswith(i + "-") for i in ids)

        if self.select and not hit(self.select):
            return False
        return not hit(self.ignore)

    def add(self, line, col, rule, msg):
        if self.on(rule):
            self.found.append((line, col, rule, msg))

    # -- whole document
    def run(self, text):
        lines = skip_regions(text.replace("\r\n", "\n").split("\n"))
        blocks = parse(lines)
        heads = [" ".join(re.sub(r"[^a-z ]", "", b.parts[0][2].lower()).split())
                 for b in blocks if b.kind == "heading"]
        self.release = any(h in CHANGELOG_HEADINGS or "release notes" in h or "changelog" in h
                           for h in heads)
        for b in blocks:
            if b.kind == "fence":
                self.code_block(b)
            elif b.kind in ("heading", "p", "li", "quote", "table"):
                self.prose(b)
        self.structure(blocks)
        self.repeated(blocks)
        return sorted(set(self.found))

    # -- code
    def code_block(self, b):
        for n, line in b.lines:
            if b.lang not in NO_LENGTH_LANGS and len(line.expandtabs(4)) > 80 and len(line.split()) > 1:
                self.add(n, 81, "code-length",
                         f"code line is {len(line.expandtabs(4))} characters; wrap at 80")
            if b.lang in PLACEHOLDER_LANGS:
                for m in ANGLE.finditer(line):
                    if m.group()[1:-1].lower() not in HTML_TAGS:
                        self.add(n, m.start() + 1, "placeholder",
                                 f"placeholder {m.group()}: use UPPER_SNAKE_CASE without angle brackets")
                for m in POSSESSIVE.finditer(line):
                    self.add(n, m.start() + 1, "placeholder",
                             f"placeholder {m.group()}: drop the your-/my- prefix and use UPPER_SNAKE_CASE")

    # -- structure across blocks
    def structure(self, blocks):
        prev, prev2, last_level, h1 = None, None, 0, 0
        for i, b in enumerate(blocks):
            if b.kind == "heading":
                n = b.parts[0][0]
                if last_level == 0 and b.level > 2:
                    self.add(n, 1, "heading-level", f"document starts at heading level {b.level}")
                elif last_level and b.level > last_level + 1:
                    self.add(n, 1, "heading-level",
                             f"heading level jumps from {last_level} to {b.level}")
                if b.level == 1:
                    h1 += 1
                    if h1 == 2:
                        self.add(n, 1, "heading-level", "second H1 in one document")
                last_level = b.level
                nxt = blocks[i + 1] if i + 1 < len(blocks) else None
                if nxt is not None and nxt.kind == "heading":
                    self.add(n, 1, "heading-empty", "heading is followed directly by another heading; add text between them")
            elif b.kind == "p" and not b.in_list and len(b.parts) == 1:
                n, col, text = b.parts[0]
                if BOLD_LINE.match(text.strip()):
                    self.add(n, col + 1, "heading-bold", "bold line used as a heading; use a real heading")
            if b.kind == "fence" or (b.kind == "li" and b.list_start):
                self.lead_in(prev, b, prev2)
            prev2, prev = prev, b

    def lead_in(self, prev, b, prev2=None):
        n = b.start if b.kind == "fence" else b.parts[0][0]
        what = "code block" if b.kind == "fence" else "list"
        if prev is None or prev.kind in ("fence", "table", "hr", "icode", "quote"):
            return
        if prev.kind == "p" and len(prev.parts) == 1 and BOLD_LINE.match(prev.parts[0][2].strip()):
            return  # a bold label line is reported once, as heading-bold
        if prev.kind == "heading" and b.kind == "li" and \
                re.sub(r"[^a-z ]", "", prev.parts[0][2].lower()).strip() in CHANGELOG_HEADINGS:
            return  # release-note groups (Added, Fixed, ...) are a template
        if prev.kind == "heading":
            self.add(n, 1, "lead-in-heading",
                     f"{what} follows a heading with no lead-in; fine when the heading gives all the context")
            return
        text = " ".join(t for _, _, t in prev.parts).rstrip()
        if prev.kind == "p" and NOTICE.match(text) and prev2 is not None and prev2.kind == "p" \
                and " ".join(t for _, _, t in prev2.parts).rstrip().endswith((".", ":")):
            return  # lead-in sentence, then a note, then the block
        if not text.endswith(":"):
            self.add(n, 1, "lead-in",
                     f"{what} is not introduced by a sentence that ends in a colon (or in a period when a note comes between)")
            return
        last = re.split(r"(?<=[.!?])\s+", text)[-1]
        words = last[:-1].split()
        alpha = [w for w in words if re.match(r"[A-Za-z]", w)]
        label = len(words) == 1 or "/" in words or (len(alpha) <= 4 and all(w[0].isupper() for w in alpha))
        if label or (words and words[-1].lower().strip("`") in FRAG_END):
            self.add(n, 1, "lead-in", f"lead-in \"{' '.join(last.split()[-6:])}\" is a fragment; use a full sentence that ends in a colon")

    def repeated(self, blocks):
        run = []
        for b in [*blocks, None]:
            key = None
            if b is not None and b.kind == "li":
                words = re.findall(r"[A-Za-z']+", mask(b.parts[0][2]))[:2]
                key = " ".join(w.lower() for w in words) if len(words) == 2 else None
            if b is not None and key is not None and run and key == run[0][0]:
                run.append((key, b))
                continue
            if len(run) >= 3:
                n = run[0][1].parts[0][0]
                self.add(n, 1, "repeated-opening",
                         f"{len(run)} list items in a row start with \"{run[0][0]}\"")
            run = [(key, b)] if key is not None and b is not None else []

    # -- prose block
    def prose(self, b):
        raw = "\n".join(t for _, _, t in b.parts)
        s = mask(raw)
        wrong_end = 0
        if b.kind == "li":
            w = WRONG_ITEM.match(raw)
            if w:
                end = raw.find("->")
                end = len(raw) if end < 0 else end
                s = "\x02" * end + s[end:]  # a wrong example is quoted on purpose
                wrong_end = end
        starts, pos = [], 0
        for _, _, t in b.parts:
            starts.append(pos)
            pos += len(t) + 1

        def at(i):
            k = bisect.bisect_right(starts, i) - 1
            n, col, _ = b.parts[k]
            return n, col + (i - starts[k]) + 1

        def emit(i, rule, msg):
            if self.on(rule):
                n, c = at(i)
                self.add(n, c, rule, msg)

        kind = b.kind
        in_table = kind == "table"
        if kind == "heading":
            self.heading(s, emit)
        self.words(s, kind, emit)
        self.punctuation(s, kind, emit)
        self.inline_code(raw, s, kind, emit, wrong_end)
        if kind in ("p", "li", "quote", "table") and self.contractions and not in_table:
            self.contraction(s, emit)
        if kind in ("p", "li", "quote"):
            self.sentences(s, emit)
        if kind in ("p", "li", "quote"):
            for m in THIS.finditer(s):
                emit(m.start(), "this-noun",
                     f"\"{m.group(1)}\" has no noun after it; add one where it reads naturally (this setting, these files)")
            for m in ONCE.finditer(s):
                emit(m.start(), "conjunction", "use \"after\" for sequence, not \"once\"")
            for m in SINCE.finditer(s):
                emit(m.start(), "conjunction", "use \"because\" for a reason, not \"since\"")
            for m in WHILE.finditer(s):
                emit(m.start(), "while", "use \"although\" for contrast; \"while\" is for time")
            for m in PASSIVE.finditer(s):
                emit(m.start(), "passive", f"passive voice candidate \"{m.group()}\"; name the actor")
        self.reference(raw, s, kind, emit, wrong_end)
        if kind != "table" and not self.release:
            for m in TIMELESS_INFO.finditer(s):
                if s[max(0, m.start() - 5):m.start()].lower() == "from ":
                    continue  # "from now on" is reported as timeless
                emit(m.start(), "timeless-info", f"\"{m.group()}\" dates the text; drop it or give a version (release notes are exempt)")

    def reference(self, raw, s, kind, emit, wrong_end=0):
        for m in LINK_URL_TEXT.finditer(raw):
            if s[m.start()] != "\x01" and m.start() >= wrong_end:
                emit(m.start(), "link-text", "use a descriptive phrase or the page title as link text, not the URL")
        for m in BOLD_VALUE.finditer(raw):
            if s[m.start()] != "\x01" and m.start() >= wrong_end:
                emit(m.start(), "bold-value", "bold is for UI labels and run-in headings; write the value in plain text")
        for m in ZONE_ABBR.finditer(s):
            emit(m.start(), "time-zone", f"don't abbreviate the time zone \"{m.group()}\"; spell it out with a UTC offset, or leave the zone out")
        for m in TIME_24H.finditer(s):
            near = s[max(0, m.start() - 40):m.end() + 40]
            if ZONE_NEAR.search(near) or ZONE_ABBR.search(near):
                emit(m.start(), "time-24h", f"use the 12-hour clock (2 PM), unless the page documents a feature that uses 24-hour time; if the UI, a command or a code sample uses 24-hour time, use that format throughout the page; \"{m.group()}\"")
        for m in ISO_DATE.finditer(s):
            emit(m.start(), "date-numeric", "write the date in words (October 5, 2026); use YYYY-MM-DD only if you must use numbers")
        for m in KEY_NAME.finditer(s):
            emit(m.start(), "key-name", f"spell out the key name: {'Control' if m.group() == 'Ctrl' else 'Command'}")
        for m in MENU_THEN.finditer(s):
            emit(m.start(), "menu-path", "write a menu path as one bold sequence, such as **File > Settings**")
        for m in IN_TOOLBAR.finditer(s):
            emit(m.start(), "ui-preposition", "the guide's table of prepositions uses \"on\" for a toolbar, as in \"on the toolbar\"")

    def heading(self, s, emit):
        if re.match(r"^(?:\d+[.)]|step\s+\d+\b)", s.strip(), re.I):
            emit(0, "heading-number", "do not number headings; use a numbered list for steps")
        for m in re.finditer(":", s):
            if s.count('"', 0, m.start()) % 2:
                continue  # a colon inside a quoted error message stays
            if not re.match(r"\s*Optional:", s):
                emit(m.start(), "heading-colon",
                     "no label and colon in headings (only the Optional: prefix); use a plain noun phrase or a bare verb. Keep a quoted error message in the heading or move it to the first sentence")
            break
        toks = [t for t in s.split() if re.fullmatch(r"[A-Za-z][A-Za-z'-]*", t.strip(".,;:?!()"))]
        toks = [t.strip(".,;:?!()") for t in toks]
        # all-caps tokens (API, SDK) are neutral: they don't make a title-case heading look sentence-case
        later = [t for t in toks[1:] if not (len(t) > 1 and t.isupper())]
        func = [t for t in later if t in FUNC_CAPS]
        allcap = len(later) >= 2 and all(t[0].isupper() and t[1:].islower() for t in later)
        caps = lambda t: t[0].isupper() and t[1:].islower()
        article = any(t in LOWER_ARTICLES and len(later) > k + 2 and caps(later[k + 1])
                      and caps(later[k + 2]) for k, t in enumerate(later))
        two_word = len(toks) == 2 and caps(toks[0]) and caps(toks[1]) \
            and toks[1].lower() in TITLE_WORDS
        if func or allcap or article or two_word:
            emit(0, "heading-case", "use sentence case in headings (capitalize only the first word and proper nouns)")

    def words(self, s, kind, emit):
        for m in self.rx.finditer(s):
            term = " ".join(m.group().lower().split())
            canon, guidance, repl = self.lookup[term]
            if canon in ("&", "and/or") and kind == "table":
                continue
            if m.group()[0].isupper() and not any(c.isupper() for c in canon) \
                    and not self.sentence_start(s, m.start()):
                continue
            skip = CONTEXT_SKIP.get(term)
            if skip:
                if skip[0] and re.search(skip[0], s[max(0, m.start() - 12):m.start()], re.I):
                    continue
                if skip[1] and re.search(skip[1], s[m.end():m.end() + 14], re.I):
                    continue
            if term == "should" and OUTPUT_INTRO.search(s[max(0, m.start() - 5):m.end() + 6]):
                continue  # reported once as output-intro
            rule = TERM_GROUPS.get(canon, TERM_GROUPS.get(term, "word-list"))
            msg = f"\"{m.group()}\": {guidance}" + (f" (use: {repl})" if repl else "")
            emit(m.start(), rule, msg)
        for m in ACCESS.finditer(s):
            emit(m.start(), "word-list", f"\"{m.group()}\": use a plainer verb (see, edit, find, use, view, read)")
        for m in TYPE_VERB.finditer(s):
            emit(m.start(), "word-list", "\"type\": prefer enter for text entry")
        for m in READ_ONLY.finditer(s):
            before = s[max(0, m.start() - 6):m.start()].strip().lower()
            if m.group().lower().strip() == "read only" and not (
                    before.endswith(("is", "are", "be")) or self.sentence_start(s, m.start())):
                continue
            emit(m.start(), "word-list", "\"read only\": hyphenate as read-only")
        for m in POSITION.finditer(s):
            emit(m.start(1) if m.group(1) else m.start(2), "position",
                 "avoid above/below for position in the document; use preceding, following or a link")
        for m in OVERCLAIM.finditer(s):
            emit(m.start(), "overclaim",
                 "do not promise protection or safety; say what the feature does (helps protect, checks)")
        for m in SECURE_VERB.finditer(s):
            if re.search(r"(?<![\w-])helps?\s+(?:to\s+)?$", s[max(0, m.start() - 12):m.start()], re.I):
                continue  # "helps prevent" is the wording the guide recommends
            if s.count('"', 0, m.start()) % 2:
                continue
            a = max(s.rfind(". ", 0, m.start()), s.rfind("\n", 0, m.start())) + 1
            b = s.find(". ", m.end())
            if SECURITY_NOUN.search(s[a:len(s) if b < 0 else b]):
                emit(m.start(), "overclaim",
                     f"\"{m.group()}\" promises security; say what the feature does (helps prevent, checks, blocks the call)")
        for m in OUTPUT_INTRO.finditer(s):
            emit(m.start(), "output-intro",
                 "show the output and introduce it with \"The output is similar to the following:\"")

    @staticmethod
    def sentence_start(s, i):
        j = i - 1
        while j >= 0 and s[j] in " \t\n\"'([\x02*_":
            j -= 1
        return j < 0 or s[j] in ".!?:|"

    def punctuation(self, s, kind, emit):
        for m in SEMICOLON.finditer(s):
            if kind == "table" or s.count('"', 0, m.start()) % 2:
                continue  # table cells and quoted examples
            if CONJ_ADVERB.match(s, m.end()):
                continue  # the guide prefers a semicolon before "therefore" and similar
            sent_start = max(s.rfind(". ", 0, m.start()), s.rfind("\n", 0, m.start())) + 1
            sent_end = s.find(". ", m.end())
            sent = s[sent_start:len(s) if sent_end < 0 else sent_end]
            if sent.count(";") >= 2 and "," in sent:
                continue  # a series of long items with their own punctuation
            emit(m.start(), "semicolon",
                 "avoid semicolons; use two sentences or a comma (the guide allows one before therefore, or in a series with commas)")
        for m in EXCLAMATION.finditer(s):
            emit(m.start(), "exclamation", "no exclamation marks")
        for m in DASH.finditer(s):
            emit(m.start(), "dash",
                 "no en dash, double hyphen or spaced em dash; use an unspaced em dash, a comma, parentheses or a new sentence")
        for m in CURLY.finditer(s):
            emit(m.start(), "curly-quote", "use straight quotes")
        if kind != "table":
            for m in ELLIPSIS.finditer(s):
                emit(m.start(), "ellipsis", "no ellipsis in prose")
        for m in NUMBER.finditer(s):
            emit(m.start(), "number-comma", f"write {int(m.group()):,} with a thousands separator")
        for m in NON_COMPOUND.finditer(s):
            emit(m.start(), "non-compound", f"the guide writes this one closed: non{m.group(1)} (keep the hyphen if the document consistently uses it)")

    def contraction(self, s, emit):
        for m in NEG_RX.finditer(s):
            if s.count('"', 0, m.start()) % 2:
                continue
            key = " ".join(m.group().lower().split())
            emit(m.start(), "contraction", f"use the contraction \"{NEGATIONS[key]}\" for \"{m.group()}\"")

    def sentences(self, s, emit):
        parts, last = [], 0
        for m in SENT_SPLIT.finditer(s):
            parts.append((last, s[last:m.start() + 1]))
            last = m.end()
        parts.append((last, s[last:]))
        openers = []
        for i, sent in parts:
            toks = [t for t in re.split(r"[\s\x02]+", sent) if re.search(r"[A-Za-z0-9\x01]", t)]
            if len(toks) > 25:
                emit(i, "sentence-length", f"sentence has {len(toks)} words; keep it to 25 or fewer")
            m = re.match(r"\s*If\s+([^,]*),\s*(?!then\b)(\S+)", sent)
            if m and len(m.group(1).split()) >= 3:
                emit(i, "if-then", "consider adding \"then\" after the if clause (a short imperative can skip it)")
            w = [x.lower() for x in re.findall(r"[A-Za-z']+", sent)[:2]]
            openers.append((i, " ".join(w) if len(w) == 2 else None))
        run = []
        for i, key in openers + [(0, None)]:
            if run and key == run[0][1]:
                run.append((i, key))
                continue
            if len(run) >= 3:
                emit(run[0][0], "repeated-opening",
                     f"{len(run)} sentences in a row start with \"{run[0][1]}\"")
            run = [(i, key)] if key else []

    def inline_code(self, raw, s, kind, emit, wrong_end=0):
        for m in CODE_SPAN.finditer(raw):
            if m.start() < wrong_end:
                continue  # a wrong example is quoted on purpose
            code = m.group(2).strip()
            if kind != "table" and kind != "heading" and FILE_LIKE.match(code):
                before = s[:m.start()].rstrip()
                nxt = re.match(r"\s*([A-Za-z]+)", s[m.end():])
                prev_word = re.search(r"([A-Za-z]+)$", before)
                if before and s.count('"', 0, m.start()) % 2 == 0 and not (nxt and nxt.group(1).lower() in ("file", "files", "directory", "folder")) \
                        and not (prev_word and prev_word.group(1).lower() in ("file", "files", "named", "called", "directory", "folder", "path")):
                    emit(m.start(), "file-noun", f"add a noun after the file name: the `{code}` file")
            if re.search(r"[\s=]", code):
                for a in ANGLE.finditer(code):
                    if a.group()[1:-1].lower() not in HTML_TAGS:
                        emit(m.start(), "placeholder", f"placeholder {a.group()}: use UPPER_SNAKE_CASE without angle brackets")
            if re.search(r"[\s=/~]", code) or re.fullmatch(r"(?:YOUR|MY)_[A-Z_]+", code):
                for a in POSSESSIVE.finditer(code):
                    emit(m.start(), "placeholder", f"placeholder {a.group()}: drop the your-/my- prefix and use UPPER_SNAKE_CASE")


def check_text(text, **kw):
    return Checker(**kw).run(text)


# ---------------------------------------------------------------- self-test

# (name, rule, expected to fire, markdown, extra Checker kwargs)
CASES = [
    ("word: tarball", "word-list", True, "Download the tarball first.\n", {}),
    ("word: tar file ok", "word-list", False, "Download the tar file first.\n", {}),
    ("word: config in prose", "word-list", True, "Edit your user config before you start.\n", {}),
    ("word: config.toml ok", "word-list", False, "Edit config.toml before you start.\n", {}),
    ("word: simply", "word-list", True, "Simply run the installer.\n", {}),
    ("word: Simple Mail ok", "word-list", False, "Use the Simple Mail service.\n", {}),
    ("word: via", "word-list", True, "Install the package via the script.\n", {}),
    ("word: term in code ok", "word-list", False, "Run `just build` to build.\n", {}),
    ("word: and/or", "word-list", True, "Set a flag and/or a key.\n", {}),
    ("word: & in table ok", "word-list", False, "| A & B | C |\n|---|---|\n", {}),
    ("word: log in", "word-list", True, "Log in to the service.\n", {}),
    ("word: we in a reader task", "word-list", True, "Next, we run the build.\n", {}),
    ("word: we recommend ok", "word-list", False, "For advice, we recommend the second option.\n", {}),
    ("word: We recommend ok", "word-list", False, "We recommend the second option.\n", {}),
    ("word: access verb", "word-list", True, "The script can access the credentials.\n", {}),
    ("word: access noun ok", "word-list", False, "You need access to the server.\n", {}),
    ("modal: should", "modal", True, "The value should be positive.\n", {}),
    ("modal: must ok", "modal", False, "The value must be positive.\n", {}),
    ("modal: May 5 ok", "modal", False, "The release shipped on May 5.\n", {}),
    ("timeless: currently", "timeless", True, "The tool currently supports two modes.\n", {}),
    ("timeless: as soon as ok", "timeless", False, "Stop as soon as the call returns.\n", {}),
    ("position: below", "position", True, "The example below shows the call.\n", {}),
    ("position: below threshold ok", "position", False, "The value falls below the threshold.\n", {}),
    ("output-intro: you should see", "output-intro", True, "You should see `OK`.\n", {}),
    ("output-intro: similar ok", "output-intro", False, "The output is similar to the following:\n", {}),
    ("contraction: does not", "contraction", True, "The file does not exist.\n", {}),
    ("contraction: doesn't ok", "contraction", False, "The file doesn't exist.\n", {}),
    ("contraction: cannot", "contraction", True, "The kernel cannot create it.\n", {}),
    ("contraction: quoted error ok", "contraction", False, "The log says \"file does not exist\" here.\n", {}),
    ("contraction: option off", "contraction", False, "The file does not exist.\n", {"contractions": False}),
    ("semicolon: prose", "semicolon", True, "Try again; do not retry.\n", {}),
    ("semicolon: code ok", "semicolon", False, "Run `a; b` twice.\n", {}),
    ("semicolon: entity ok", "semicolon", False, "Use the &amp; entity.\n", {}),
    ("dash: em dash", "dash", True, "It works — mostly.\n", {}),
    ("curly-quote", "curly-quote", True, "Click “OK”.\n", {}),
    ("exclamation", "exclamation", True, "It works! Now go.\n", {}),
    ("ellipsis in prose", "ellipsis", True, "Wait... it runs.\n", {}),
    ("number-comma: 1000 bytes", "number-comma", True, "It sends 1000 bytes.\n", {}),
    ("number-comma: 1,000 ok", "number-comma", False, "It sends 1,000 bytes.\n", {}),
    ("number-comma: year ok", "number-comma", False, "It shipped in 2026.\n", {}),
    ("non-compound: non-interactive, info level", "non-compound", True, "A non-interactive call.\n", {"info": True}),
    ("non-compound: off by default", "non-compound", False, "A non-interactive call.\n", {}),
    ("non-compound: noninteractive ok", "non-compound", False, "A noninteractive call.\n", {"info": True}),
    ("sentence-length: 30 words", "sentence-length", True,
     "One two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
     "sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour "
     "twentyfive twentysix twentyseven.\n", {}),
    ("sentence-length: short ok", "sentence-length", False, "Run the tool. It stops.\n", {}),
    ("this-noun: bare this", "this-noun", True, "Add this to the file.\n", {}),
    ("this-noun: this setting ok", "this-noun", False, "Add this setting to the file.\n", {}),
    ("file-noun: bare file name", "file-noun", True, "Open `config.toml` in an editor.\n", {}),
    ("file-noun: quoted example ok", "file-noun", False, "Write \"edit `a.json` now\" in the note.\n", {}),
    ("file-noun: with file ok", "file-noun", False, "Open the `config.toml` file in an editor.\n", {}),
    ("conjunction: once", "conjunction", True, "Remove it once you install the package.\n", {}),
    ("conjunction: once per day ok", "conjunction", False, "It runs once per day.\n", {}),
    ("conjunction: since because", "conjunction", True, "Install it, since it can't run otherwise.\n", {}),
    ("conjunction: since 2020 ok", "conjunction", False, "It has existed since 2020.\n", {}),
    ("heading-number", "heading-number", True, "# T\n\n### 1. Download it\n\nText.\n", {}),
    ("heading-colon", "heading-colon", True, "# T\n\n## Fix: install it\n\nText.\n", {}),
    ("heading-case: title case", "heading-case", True, "# How To Create An Instance\n", {}),
    ("heading-case: sentence ok", "heading-case", False, "# How to create an instance\n", {}),
    ("heading-case: product name ok", "heading-case", False, "# Windows Subsystem for Linux\n", {}),
    ("heading-empty", "heading-empty", True, "# T\n\nText.\n\n## A\n### B\n\nText.\n", {}),
    ("heading-empty: H1 then H2", "heading-empty", True, "# T\n## A\n\nText.\n", {}),
    ("heading-empty: H1 then text ok", "heading-empty", False, "# T\n\nText.\n\n## A\n\nText.\n", {}),
    ("heading-colon: quoted error ok", "heading-colon", False,
     "# T\n\n## Troubleshooting \"engine unavailable: bwrap not found\"\n\nText.\n", {}),
    ("heading-colon: code font ok", "heading-colon", False,
     "# T\n\n## Fix the `error: not found` message\n\nText.\n", {}),
    ("heading-colon: colon after quote still fires", "heading-colon", True,
     "# T\n\n## Fix \"x\": the error\n\nText.\n", {}),
    ("heading-case: acronym in title case", "heading-case", True, "# Utility Call API Reference\n", {}),
    ("heading-case: acronym after the, product-like name ok", "heading-case", False, "# Rotating the Relay API Key\n", {}),
    ("heading-case: acronym in sentence case ok", "heading-case", False, "# Rotate the relay API key\n", {}),
    ("heading-case: Getting Started", "heading-case", True, "# Getting Started\n", {}),
    ("heading-case: Add a Model Provider", "heading-case", True, "# Add a Model Provider\n", {}),
    ("heading-case: Claude Code ok", "heading-case", False, "# Claude Code\n", {}),
    ("heading-case: Add a model provider ok", "heading-case", False, "# Add a model provider\n", {}),
    ("heading-case: Install the Windows Subsystem for Linux ok", "heading-case", False,
     "# Install the Windows Subsystem for Linux\n", {}),
    ("overclaim: sandbox prevents", "overclaim", True,
     "The sandbox prevents workflow scripts from reading files.\n", {}),
    ("overclaim: ensures near secure", "overclaim", True,
     "This setting ensures that your data stays secure.\n", {}),
    ("overclaim: helps prevent ok", "overclaim", False,
     "The sandbox helps prevent scripts from reading files.\n", {}),
    ("overclaim: prevents without security noun ok", "overclaim", False,
     "The lock file prevents duplicate writes.\n", {}),
    ("overclaim: security noun in another sentence ok", "overclaim", False,
     "The sandbox is on. The cache prevents duplicate writes.\n", {}),
    ("link-text: raw URL", "link-text", True,
     "See [https://status.example.com](https://status.example.com) for updates.\n", {}),
    ("link-text: descriptive ok", "link-text", False,
     "See the [status page](https://status.example.com) for updates.\n", {}),
    ("link-text: URL in code ok", "link-text", False,
     "Write `[https://a.example](b)` in the file.\n", {}),
    ("time-24h: 24-hour with UTC", "time-24h", True, "Maintenance runs 02:00 to 04:00 UTC.\n", {}),
    ("time-24h: 24-hour with KST abbreviation", "time-24h", True, "It starts at 11:00 KST.\n", {}),
    ("time-24h: 12-hour ok", "time-24h", False, "Maintenance runs 2 AM to 4 AM UTC.\n", {}),
    ("time-24h: 24-hour without a zone ok", "time-24h", False, "The log shows 14:03 here.\n", {}),
    ("time-24h: timestamp ok", "time-24h", False, "At 2026-10-05T02:00:00 UTC it began.\n", {}),
    ("time-zone: KST", "time-zone", True, "The window is 11 AM KST.\n", {}),
    ("time-zone: UTC label ok", "time-zone", False, "It is Korea Standard Time (UTC+9).\n", {}),
    ("time-zone: in code ok", "time-zone", False, "Set `TZ=KST` first.\n", {}),
    ("date-numeric: ISO date", "date-numeric", True, "Released 2026-10-05.\n", {}),
    ("date-numeric: words ok", "date-numeric", False, "Released October 5, 2026.\n", {}),
    ("date-numeric: code ok", "date-numeric", False, "Run `ls 2026-10-05` now.\n", {}),
    ("date-numeric: version ok", "date-numeric", False, "Use version 2026-13-45 of it.\n", {}),
    ("key-name: Ctrl", "key-name", True, "Press Ctrl+C to stop.\n", {}),
    ("key-name: Control ok", "key-name", False, "Press Control+C to stop.\n", {}),
    ("key-name: in code ok", "key-name", False, "Run `ctrl --help` now.\n", {}),
    ("menu-path: select File, then Settings", "menu-path", True, "Select File, then Settings.\n", {}),
    ("menu-path: bold labels", "menu-path", True, "Select **File**, then **Settings**.\n", {}),
    ("menu-path: arrow notation ok", "menu-path", False, "Select **File > Settings**.\n", {}),
    ("menu-path: two actions ok", "menu-path", False, "Click **Next**, then click **Finish**.\n", {}),
    ("ui-preposition: In the toolbar", "ui-preposition", True, "In the toolbar, select **Run**.\n", {}),
    ("ui-preposition: On the toolbar ok", "ui-preposition", False, "On the toolbar, select **Run**.\n", {}),
    ("bold-value: bold number", "bold-value", True, "The limit is **18 MiB** per file.\n", {}),
    ("bold-value: run-in label ending in a period ok", "bold-value", False, "- **25 words or fewer.** Keep it short.\n", {}),
    ("bold-value: period after the bold span still fires", "bold-value", True, "The limit is **18 MiB**.\n", {}),
    ("bold-value: bold label ok", "bold-value", False, "Select **Settings** to open it.\n", {}),
    ("bold-value: in code ok", "bold-value", False, "Write `**2` in the file.\n", {}),
    ("heading-level: skip", "heading-level", True, "# T\n\nText.\n\n### C\n\nText.\n", {}),
    ("heading-level: starts at H3", "heading-level", True, "### A\n\nText.\n", {}),
    ("heading-level: starts at H2 ok", "heading-level", False, "## A\n\nText.\n", {}),
    ("lead-in: Added list ok", "lead-in", False, "## Added\n\n- One.\n- Two.\n", {}),
    ("semicolon: quoted ok", "semicolon", False, "Write \"stop; go\" here.\n", {}),
    ("heading-bold", "heading-bold", True, "Text.\n\n**Setup**\n\nText.\n", {}),
    ("lead-in: missing colon", "lead-in", True, "Install it.\n\n```sh\nmake\n```\n", {}),
    ("lead-in: fragment label", "lead-in", True, "Fedora:\n\n```sh\ndnf install x\n```\n", {}),
    ("lead-in: heading then list is not a default finding", "lead-in", False,
     "## Before you begin\n\n- One.\n- Two.\n", {}),
    ("lead-in-heading: off by default", "lead-in-heading", False,
     "## Before you begin\n\n- One.\n- Two.\n", {}),
    ("lead-in-heading: list, info level", "lead-in-heading", True,
     "## Before you begin\n\n- One.\n- Two.\n", {"info": True}),
    ("lead-in-heading: code block, info level", "lead-in-heading", True,
     "## Install\n\n```sh\nmake\n```\n", {"info": True}),
    ("lead-in: heading then code block is not a default finding", "lead-in", False,
     "## Install\n\n```sh\nmake\n```\n", {}),
    ("lead-in: paragraph without colon then list", "lead-in", True, "Install it.\n\n- One.\n- Two.\n", {}),
    ("lead-in: the following ok", "lead-in", False, "Do the following:\n\n- One.\n- Two.\n", {}),
    ("lead-in: use the following ok", "lead-in", False, "Use the following:\n\n```sh\nmake\n```\n", {}),
    ("this-noun: the following ok", "this-noun", False, "Add the following to the file:\n\n- One.\n", {}),
    ("word-list: the following ok", "word-list", False, "Do the following:\n\n- One.\n", {}),
    ("semicolon: before however ok", "semicolon", False, "Try the call; however, wait first.\n", {}),
    ("semicolon: series with commas ok", "semicolon", False,
     "Review the tense, voice; typos, grammar; and length.\n", {}),
    ("semicolon: table cell ok", "semicolon", False, "| a; b | c |\n|---|---|\n", {}),
    ("dash: unspaced em dash ok", "dash", False, "It works\u2014mostly.\n", {}),
    ("dash: en dash", "dash", True, "It takes 5\u201310 minutes.\n", {}),
    ("dash: double hyphen", "dash", True, "It works -- mostly.\n", {}),
    ("non-compound: non-integer ok", "non-compound", False, "A non-integer value.\n", {}),
    ("non-compound: non-empty, info level", "non-compound", True, "A non-empty list.\n", {"info": True}),
    ("heading-colon: Optional prefix ok", "heading-colon", False, "# T\n\n## Optional: add a proxy\n\nText.\n", {}),
    ("wrong item: before arrow is skipped", "word-list", False, "- wrong: Simply stop. -> right: Stop it.\n", {}),
    ("wrong item: after arrow is checked", "word-list", True, "- wrong: Stop it. -> right: Simply stop.\n", {}),
    ("check-style off region is skipped", "word-list", False,
     "<!-- check-style: off -->\n\nSimply stop.\n\n<!-- check-style: on -->\n", {}),
    ("check-style on again after region", "word-list", True,
     "<!-- check-style: off -->\n\nOk.\n\n<!-- check-style: on -->\n\nSimply stop.\n", {}),
    ("lead-in: period, note, then list ok", "lead-in", False,
     "Install it.\n\nNote: The tool needs root access.\n\n- One.\n- Two.\n", {}),
    ("lead-in: period, note, then code block ok", "lead-in", False,
     "Run the installer.\n\n**Note:** It needs root access.\n\n```sh\nmake\n```\n", {}),
    ("lead-in: note with no sentence before it", "lead-in", True,
     "## Install\n\nNote: The tool needs root access.\n\n- One.\n- Two.\n", {}),
    ("lead-in: sentence ok", "lead-in", False, "Run the following command:\n\n```sh\nmake\n```\n", {}),
    ("placeholder: angle in block", "placeholder", True, "Run:\n\n```sh\nwsl --set-version <distro> 2\n```\n", {}),
    ("placeholder: UPPER ok", "placeholder", False, "Run:\n\n```sh\nwsl --set-version DISTRO 2\n```\n", {}),
    ("placeholder: your- in block", "placeholder", True, "Run:\n\n```sh\ncd your-project\n```\n", {}),
    ("placeholder: inline angle", "placeholder", True, "Run `wsl --set-version <distro> 2` now.\n", {}),
    ("placeholder: C++ template ok", "placeholder", False, "Run:\n\n```cpp\nstd::vector<Message> m;\n```\n", {}),
    ("code-length: 100 chars", "code-length", True, "Run:\n\n```sh\ncurl -fsSL " + "a" * 40 + " -o " + "b" * 40 + " --retry 3\n```\n", {}),
    ("code-length: short ok", "code-length", False, "Run:\n\n```sh\ncurl -fsSL url\n```\n", {}),
    ("code-length: single token ok", "code-length", False, "Run:\n\n```sh\n" + "a" * 100 + "\n```\n", {}),
    ("overclaim: protect you from", "overclaim", True, "This check protects you from spoofing.\n", {}),
    ("overclaim: helps protect ok", "overclaim", False, "This check helps protect you against spoofing.\n", {}),
    ("word: read only label", "word-list", True, "Read only. The agent can look.\n", {}),
    ("word: read-only ok", "word-list", False, "The mode is read-only.\n", {}),
    ("word: read only the first line ok", "word-list", False, "The tool can read only the first line.\n", {}),
    ("human-verb: refuses", "human-verb", True, "The engine refuses to start.\n", {}),
    ("info off by default: passive", "passive", False, "The file is written by the tool.\n", {}),
    ("info: passive", "passive", True, "The file is written by the tool.\n", {"info": True}),
    ("info: if without then", "if-then", True, "If the file is missing, create it.\n", {"info": True}),
    ("info: if with then ok", "if-then", False, "If the file is missing, then create it.\n", {"info": True}),
    ("placeholder: wrong item is skipped", "placeholder", False, "- wrong: `--project=<my-project>` -> right: `--project=PROJECT_ID`\n", {}),
    ("placeholder: right half is checked", "placeholder", True, "- wrong: `--project=PROJECT_ID` -> right: `--project=<my-project>`\n", {}),
    ("file-noun: wrong item is skipped", "file-noun", False, "- wrong: `Release_Notes.md` -> right: the `release-notes.md` file\n", {}),
    ("if-then: off by default", "if-then", False, "If the file is missing, create it.\n", {}),
    ("bold-value: wrong item is skipped", "bold-value", False, "- wrong: The limit is **18 MiB**. -> right: The limit is 18 MiB.\n", {}),
    ("bold-value: right half is checked", "bold-value", True, "- wrong: The limit is 18 MiB. -> right: The limit is **18 MiB**.\n", {}),
    ("link-text: wrong item is skipped", "link-text", False, "- wrong: See [https://example.com/a](https://example.com/a). -> right: See the page.\n", {}),
    ("time-24h: wrong item is skipped", "time-24h", False, "- wrong: Maintenance runs 02:00 to 04:00 UTC. -> right: Maintenance runs 2-4 AM UTC.\n", {}),
    ("info: now in release notes ok", "timeless-info", False, "# Release notes\n\nYou can now choose a model.\n", {"info": True}),
    ("info: now in guide", "timeless-info", True, "# Guide\n\nYou can now choose a model.\n", {"info": True}),
    ("info: repeated openings", "repeated-opening", True,
     "Steps:\n\n- The agent reads files.\n- The agent writes files.\n- The agent runs tests.\n", {"info": True}),
    ("ignore by prefix", "heading-colon", False, "# T\n\n## Fix: it\n\nText.\n", {"ignore": ["heading"]}),
    ("select only one rule", "word-list", False, "Simply stop; it ends.\n", {"select": ["semicolon"]}),
]

CLEAN = """# Install the tool

Download the tar file from the releases page. The installer doesn't need root access to your system.

To install the tool, follow these steps:

1. Download the release:

   ```sh
   curl -fsSLO https://example.com/tool.tar.gz
   ```

2. Run the installer.

If the install fails, then check the log. The tool writes the log to the `~/.tool/log` directory.

## Configure the tool

Open the `config.toml` file in an editor. Set the `model` key.
"""


MESSAGE_CASES = [
    ("if-then message says consider", "if-then", "If the file is missing, create it.\n", {"info": True}, "consider adding"),
    ("time-24h message names the UI, command and code sample", "time-24h", "It starts at 11:00 KST.\n", {},
     "the UI, a command or a code sample"),
    ("time-24h message names documenting 24-hour features", "time-24h", "It starts at 11:00 KST.\n", {},
     "documents a feature that uses 24-hour time"),
    ("time-24h message says throughout the page", "time-24h", "It starts at 11:00 KST.\n", {},
     "throughout the page"),
    ("lead-in message mentions a note between", "lead-in", "Install it.\n\n- One.\n- Two.\n", {},
     "a period when a note comes between"),
    ("non-compound message allows a consistent hyphen", "non-compound", "A non-empty list.\n", {"info": True},
     "consistently uses it"),
]


def self_test():
    failed = 0
    for name, rule, expect, text, kw in CASES:
        got = any(f[2] == rule for f in check_text(text, **kw))
        if got != expect:
            failed += 1
            print(f"FAIL {name}: expected {'a' if expect else 'no'} {rule} finding, got {'one' if got else 'none'}")
    for name, rule, text, kw, want in MESSAGE_CASES:
        msgs = [f[3] for f in check_text(text, **kw) if f[2] == rule]
        if not msgs or want not in msgs[0]:
            failed += 1
            print(f"FAIL {name}: message {msgs[:1]} lacks {want!r}")
    extra = check_text(CLEAN, info=False)
    if extra:
        failed += 1
        print("FAIL clean document: " + "; ".join(f"{l}:{c} {r}" for l, c, r, _ in extra))
    total = len(CASES) + len(MESSAGE_CASES) + 1
    print(f"self-test: {total - failed}/{total} passed")
    return failed == 0


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(description="Report style findings in Markdown files (never rewrites).")
    ap.add_argument("paths", nargs="*", help="Markdown files or directories")
    ap.add_argument("--info", action="store_true", help="enable info-level checks")
    ap.add_argument("--no-contractions", action="store_true", help="skip the negation-contraction check")
    ap.add_argument("--select", default="", help="comma-separated rule ids to run (others are skipped)")
    ap.add_argument("--ignore", default="", help="comma-separated rule ids to skip")
    ap.add_argument("--self-test", action="store_true", help="run the built-in cases and exit")
    ap.add_argument("--list-rules", action="store_true", help="print rule ids and exit")
    a = ap.parse_args(argv)
    if a.list_rules:
        for k, v in RULES.items():
            print(f"{k:18} {v}")
        return 0
    if a.self_test:
        return 0 if self_test() else 1
    if not a.paths:
        ap.error("give at least one file or directory (or --self-test)")
    split = lambda v: [x.strip() for x in v.split(",") if x.strip()]
    chk_args = dict(info=a.info, contractions=not a.no_contractions,
                    select=split(a.select), ignore=split(a.ignore))
    files = []
    for p in a.paths:
        if os.path.isdir(p):
            for root, _, names in sorted(os.walk(p)):
                files += [os.path.join(root, n) for n in sorted(names) if n.endswith(".md")]
        else:
            files.append(p)
    words = build_matcher(load_word_list())
    count = 0
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            print(f"{path}: cannot read: {e.strerror}", file=sys.stderr)
            return 2
        for line, col, rule, msg in Checker(words=words, **chk_args).run(text):
            print(f"{path}:{line}:{col}: {rule}: {msg}")
            count += 1
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
