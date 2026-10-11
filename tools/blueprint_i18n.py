"""Build translated copies of a Polish Home Assistant blueprint from a string catalog.

The Polish blueprint is the source. Every source line that carries text for people
(names, descriptions, option labels, step names, notifications, comments) is a
segment in the catalog together with its translations. Building a language replaces
those segments line by line, so keys, option values, triggers, entity ids and
template logic stay exactly as in the source.

    python tools/blueprint_i18n.py extract  <blueprint> <catalog>
    python tools/blueprint_i18n.py build    <blueprint> <catalog>
    python tools/blueprint_i18n.py check    <blueprint> <catalog>

``extract`` adds new segments to the catalog (with empty translations) and lists
segments that are no longer used. ``build`` writes ``<name>_<lang>.yaml`` next to
the source. ``check`` fails when a translation is missing, a segment is stale, a
generated file is out of date, or a generated file differs from the source in
anything other than text.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from jinja2 import Environment

LANGUAGES = ("en", "de")

# Keys whose plain string values are text for people.
TEXT_KEYS = {
    "name", "description", "label", "alias", "stop", "title", "message",
    "tytul", "tresc", "reason", "growth_note",
}
# Mappings whose values (not keys) are labels shown to people.
LABEL_MAPS = {"mower_error_names", "mower_state_names"}

POLISH_LETTERS = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")
IDENTIFIER = re.compile(r"^[a-z0-9_.\-]*$")
JINJA = re.compile(r"{{|{%|{#")


class _Loader(yaml.SafeLoader):
    """Safe loader that accepts the blueprint !input tag."""


_Loader.add_constructor("!input", lambda loader, node: {"!input": loader.construct_scalar(node)})


def load_yaml(text: str):
    return yaml.load(text, Loader=_Loader)  # noqa: S506 - SafeLoader subclass


def _is_text_scalar(path: tuple, value: str) -> bool:
    key = path[-1] if path else None
    parent = path[-2] if len(path) > 1 else None
    return key in TEXT_KEYS or parent in LABEL_MAPS or bool(JINJA.search(value))


def _text_scalars(node, path=(), seen=None):
    """Yield scalar nodes that can carry translatable text, with their key path."""
    if seen is None:
        seen = set()
    if id(node) in seen:
        return
    seen.add(id(node))
    if isinstance(node, yaml.MappingNode):
        for key_node, value_node in node.value:
            yield from _text_scalars(value_node, path + (key_node.value,), seen)
    elif isinstance(node, yaml.SequenceNode):
        for item in node.value:
            yield from _text_scalars(item, path + ("[]",), seen)
    elif isinstance(node, yaml.ScalarNode) and node.tag == "tag:yaml.org,2002:str":
        if _is_text_scalar(path, node.value):
            yield node


LETTERS = re.compile(r"[^\W\d_]")


def _is_text_data(value: str) -> bool:
    """Template text outside tags: words for people, not a bare code like ``mower_away``.

    A single word between two tags is text when it is surrounded by spaces
    (``}} o {{``, ``}} godz. {{``); codes are written right next to the tag.
    """
    stripped = value.strip()
    if not LETTERS.search(stripped):
        return False
    if not IDENTIFIER.match(stripped):
        return True
    return value.startswith(" ") and value.endswith(" ")


def _is_text_literal(literal: str, previous: str) -> bool:
    """A string literal inside a tag that is shown to people.

    ``previous`` is the token before the literal: ``:`` marks a dictionary value,
    for example a label in ``{'cloudy': 'pochmurno'}``.
    """
    if not LETTERS.search(literal):
        return False
    if POLISH_LETTERS.search(literal) or " " in literal.strip() or literal != literal.strip() or "%" in literal:
        return True
    return previous == ":"


def _marker(kind: str, value: str) -> str:
    """Kind of a lexer token, with the operator itself for operators."""
    return value if kind == "operator" else kind


def _text_lines(raw: str) -> set[int]:
    """0-based lines of a template that carry text for people."""
    if not JINJA.search(raw):
        return {n for n, line in enumerate(raw.split("\n")) if LETTERS.search(line)}
    try:
        tokens = list(Environment().lex(raw))
    except Exception:  # noqa: BLE001 - not a valid template: treat every line as text
        return {n for n, line in enumerate(raw.split("\n")) if LETTERS.search(line)}
    lines = set()
    previous_kind = ""
    for lineno, kind, value in tokens:
        if kind == "data":
            offset = 0
            for part in value.split("\n"):
                if _is_text_data(part):
                    lines.add(lineno - 1 + offset)
                offset += 1
        elif kind == "string":
            literal = value[1:-1]
            if _is_text_literal(literal, previous_kind):
                lines.add(lineno - 1 + value.count("\n"))
        if kind != "whitespace":
            previous_kind = _marker(kind, value)
    return lines


@dataclass(frozen=True)
class Segment:
    line: int  # 0-based line number in the source
    start: int  # column where the translatable text starts
    end: int  # column where it ends
    text: str


def segments(source: str) -> list[Segment]:
    """Return the translatable text of the source, one segment per source line."""
    lines = source.split("\n")
    root = yaml.compose(source, Loader=_Loader)
    found: dict[int, Segment] = {}

    def add(number: int, col: int, end: int | None = None) -> None:
        line = lines[number]
        text = (line[col:end] if end is not None else line[col:]).rstrip()
        col += len(text) - len(text.lstrip())
        text = text.lstrip()
        if text:
            found[number] = Segment(number, col, col + len(text), text)

    for node in _text_scalars(root):
        start, end = node.start_mark, node.end_mark
        if node.style in ("|", ">"):
            content, indent = [], None
            for number in range(start.line + 1, len(lines)):
                line = lines[number]
                if not line.strip():
                    content.append(number)
                    continue
                current = len(line) - len(line.lstrip())
                if indent is None:
                    indent = current
                if current < indent:
                    break
                content.append(number)
            if indent is None:
                continue
            raw = "\n".join(lines[n][indent:] for n in content)
            for offset in _text_lines(raw):
                if offset < len(content):
                    add(content[offset], indent)
        elif start.line == end.line:
            if _text_lines(node.value):
                add(start.line, start.column, end.column)
        else:
            for number in range(start.line, end.line + 1):
                line = lines[number]
                col = start.column if number == start.line else len(line) - len(line.lstrip())
                stop = end.column if number == end.line else None
                if LETTERS.search(line[col:stop] if stop is not None else line[col:]):
                    add(number, col, stop)
    for number, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") and number not in found:
            add(number, len(line) - len(stripped))
    return [found[n] for n in sorted(found)]


def load_catalog(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("segments", [])


def save_catalog(path: Path, entries: list[dict]) -> None:
    out = [
        "# Translations of the Polish blueprint, one entry per source line with text.",
        "# Edit the translations, then run: python tools/blueprint_i18n.py build <blueprint> <catalog>",
        "segments:",
    ]
    for entry in entries:
        out.append(f"  - pl: {json.dumps(entry['pl'], ensure_ascii=False)}")
        for lang in LANGUAGES:
            out.append(f"    {lang}: {json.dumps(entry.get(lang) or '', ensure_ascii=False)}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def output_path(source_path: Path, lang: str) -> Path:
    return source_path.with_name(f"{source_path.stem}_{lang}{source_path.suffix}")


def build_text(source: str, source_path: Path, catalog: list[dict], lang: str) -> tuple[str, list[str]]:
    table = {entry["pl"]: entry.get(lang) or "" for entry in catalog}
    lines = source.split("\n")
    missing = []
    for seg in segments(source):
        translated = table.get(seg.text)
        if not translated:
            missing.append(seg.text)
            continue
        line = lines[seg.line]
        lines[seg.line] = line[: seg.start] + translated + line[seg.end:]
    text = "\n".join(lines)
    name = source_path.name
    text = re.sub(
        r"(source_url: \S*/)" + re.escape(name),
        lambda m: m.group(1) + output_path(source_path, lang).name,
        text,
    )
    return text, missing


def _logic_tokens(value: str) -> list[tuple[str, str, str]]:
    """Template tokens without data and whitespace, each with the kind of the token before it."""
    result = []
    previous = ""
    for _, kind, token in Environment().lex(value):
        if kind in ("data", "whitespace"):
            continue
        result.append((kind, token, previous))
        previous = _marker(kind, token)
    return result


def same_template_logic(source: str, translated: str) -> bool:
    """True when only text differs: template text and string literals that hold text."""
    left, right = _logic_tokens(source), _logic_tokens(translated)
    if len(left) != len(right):
        return False
    for (kind, token, previous), (other_kind, other_token, _) in zip(left, right):
        if kind != other_kind:
            return False
        if token == other_token:
            continue
        if kind == "string" and _is_text_literal(token[1:-1], previous):
            continue
        if kind == "string" and not IDENTIFIER.match(token[1:-1]) and not LETTERS.search(token[1:-1]):
            continue  # separators such as ',' in replace('.', ',')
        return False
    return True


def structure_differences(source, translated, path="") -> list[str]:
    """Differences other than text between the parsed source and a translation."""
    problems = []
    if type(source) is not type(translated):
        return [f"{path}: type {type(source).__name__} != {type(translated).__name__}"]
    if isinstance(source, dict):
        if list(source) != list(translated):
            return [f"{path}: keys differ"]
        for key in source:
            sub = f"{path}.{key}"
            if path.rsplit(".", 1)[-1] in LABEL_MAPS and isinstance(source[key], str):
                continue
            problems += structure_differences(source[key], translated[key], sub)
    elif isinstance(source, list):
        if len(source) != len(translated):
            return [f"{path}: list length {len(source)} != {len(translated)}"]
        for index, (a, b) in enumerate(zip(source, translated)):
            problems += structure_differences(a, b, f"{path}[{index}]")
    elif isinstance(source, str):
        key = path.rsplit(".", 1)[-1].split("[")[0]
        if JINJA.search(source) or JINJA.search(translated):
            try:
                if not same_template_logic(source, translated):
                    problems.append(f"{path}: template logic differs")
            except Exception as err:  # noqa: BLE001
                problems.append(f"{path}: template does not parse ({err})")
        elif key not in TEXT_KEYS and source != translated and key != "source_url":
            problems.append(f"{path}: value changed ({source!r} -> {translated!r})")
    elif source != translated:
        problems.append(f"{path}: {source!r} != {translated!r}")
    return problems


def cmd_extract(source_path: Path, catalog_path: Path) -> int:
    source = source_path.read_text(encoding="utf-8")
    catalog = load_catalog(catalog_path)
    known = {entry["pl"]: entry for entry in catalog}
    ordered, added = [], 0
    for seg in segments(source):
        if seg.text in known:
            entry = known.pop(seg.text)
            if entry not in ordered:
                ordered.append(entry)
        elif not any(e["pl"] == seg.text for e in ordered):
            ordered.append({"pl": seg.text, **{lang: "" for lang in LANGUAGES}})
            added += 1
    for stale in known.values():
        print("stale (removed):", stale["pl"])
    save_catalog(catalog_path, ordered)
    print(f"segments: {len(ordered)}, new: {added}, removed: {len(known)}")
    return 0


def cmd_build(source_path: Path, catalog_path: Path) -> int:
    source = source_path.read_text(encoding="utf-8")
    catalog = load_catalog(catalog_path)
    failed = False
    for lang in LANGUAGES:
        text, missing = build_text(source, source_path, catalog, lang)
        if missing:
            failed = True
            print(f"{lang}: {len(missing)} missing translations, first: {missing[0]!r}")
            continue
        output_path(source_path, lang).write_text(text, encoding="utf-8", newline="\n")
        print(f"{lang}: written {output_path(source_path, lang)}")
    return 1 if failed else 0


def check(source_path: Path, catalog_path: Path) -> list[str]:
    source = source_path.read_text(encoding="utf-8")
    catalog = load_catalog(catalog_path)
    problems = []
    used = {seg.text for seg in segments(source)}
    for entry in catalog:
        if entry["pl"] not in used:
            problems.append(f"stale segment: {entry['pl']!r}")
    parsed_source = load_yaml(source)
    for lang in LANGUAGES:
        text, missing = build_text(source, source_path, catalog, lang)
        problems += [f"{lang}: missing translation for {m!r}" for m in missing]
        if missing:
            continue
        path = output_path(source_path, lang)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            problems.append(f"{lang}: {path.name} is out of date, run build")
        leftovers = [line.strip() for line in text.split("\n") if POLISH_LETTERS.search(line)]
        problems += [f"{lang}: Polish text left: {line!r}" for line in leftovers]
        problems += [f"{lang}: {p}" for p in structure_differences(parsed_source, load_yaml(text))]
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in {"extract", "build", "check"}:
        print(__doc__)
        return 2
    source_path, catalog_path = Path(argv[2]), Path(argv[3])
    if argv[1] == "extract":
        return cmd_extract(source_path, catalog_path)
    if argv[1] == "build":
        return cmd_build(source_path, catalog_path)
    problems = check(source_path, catalog_path)
    for problem in problems:
        print(problem)
    print("OK" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
