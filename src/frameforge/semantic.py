"""Generic, bounded evidence evaluator. No engine or project-specific patterns."""
import re
from pathlib import Path


def mask_comments(source, language):
    """Mask real C# or Lua comments while preserving quoted string contents and line numbers."""
    if language == "csharp":
        pattern = re.compile(
            r'(?P<string>(?P<raw_delimiter>"{3,})[\s\S]*?(?P=raw_delimiter)|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
            r'|(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)'
        )
    elif language == "lua":
        pattern = re.compile(
            r'(?P<long_string>\[(?P<eq>=*)\[[\s\S]*?\](?P=eq)\])'
            r'|(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
            r'|(?P<comment>--\[(?P<comment_eq>=*)\[[\s\S]*?\](?P=comment_eq)\]|--[^\n]*)'
        )
    else:
        raise ValueError("unsupported comment masking language")
    return pattern.sub(
        lambda match: re.sub(r'[^\n]', ' ', match.group())
        if match.group("comment") else match.group(),
        source,
    )


def evaluate(root, rule):
    """Observe declared literals across bounded source paths; never claim control-flow compliance."""
    root = Path(root).resolve()
    sources = []
    for relative in rule["paths"]:
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 500_000:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        # Comment filtering is intentionally conservative; not a language parser.
        source = mask_comments(source, rule["language"])
        sources.append((relative, source))

    if not sources:
        return {
            "plugin_id": rule["plugin_id"], "check_id": rule["id"],
            "standard_topic": rule["topic"], "status": "not_evaluated",
            "evidence": [], "missing_tokens": [],
            "recommendation": rule["recommendation"], "confidence": "no_source",
            "activation": "explicit_project_rule",
        }

    evidence = []
    missing = []
    for token in rule["tokens"]:
        match = next((
            {"path": relative, "line": line_number, "token": token}
            for relative, source in sources
            for line_number, line in enumerate(source.splitlines(), 1)
            if token in line
        ), None)
        if match:
            evidence.append(match)
        else:
            missing.append(token)
    return {
        "plugin_id": rule["plugin_id"], "check_id": rule["id"],
        "standard_topic": rule["topic"],
        "status": "review_needed" if missing else "pattern_observed_control_flow_unverified",
        "evidence": evidence, "missing_tokens": missing,
        "recommendation": rule["recommendation"],
        "confidence": "bounded_literal_scan",
        "activation": "explicit_project_rule",
    }

def validate_rules(rules):
    if not isinstance(rules, list):
        raise ValueError("semantic_rules must be a list")
    if len(rules) > 100:
        raise ValueError("too many semantic rules")
    ids = set()
    for rule in rules:
        if not isinstance(rule, dict) or not all(
            isinstance(rule.get(k), str) and bool(rule[k].strip())
            for k in ("id", "plugin_id", "topic", "recommendation")
        ) or any(rule[k] != rule[k].strip() for k in ("id", "plugin_id", "topic")):
            raise ValueError("invalid semantic rule identity")
        if rule["id"] in ids:
            raise ValueError("duplicate semantic rule id")
        ids.add(rule["id"])
        if rule.get("language") not in ("csharp", "lua"):
            raise ValueError("unsupported semantic rule language")
        for field in ("paths", "tokens"):
            values = rule.get(field)
            if not isinstance(values, list) or not values or len(values) > 20 or not all(
                isinstance(v, str) and 0 < len(v) <= 256
                and (field != "tokens" or bool(v.strip()))
                for v in values
            ):
                raise ValueError("invalid semantic rule " + field)
        if any(Path(v).is_absolute() or re.match(r"^[A-Za-z]:", v) or ".." in Path(v.replace("\\", "/")).parts or "\x00" in v or "\\" in v for v in rule["paths"]):
            raise ValueError("invalid semantic rule path")
    return rules
