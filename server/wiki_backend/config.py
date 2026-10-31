# SPDX-License-Identifier: Apache-2.0
"""Instance configuration: ``manifold.yaml`` at the root of the instance repository.

The file holds the settings that identify an instance and the registry of its
components.  It replaces the component list that used to be hard-coded in
``handoff.py`` and the slug list that was text-edited inside ``wiki/CLAUDE.md``.

    version: 1
    name: Acme Engineering Wiki
    server_name: manifold
    brand:
      accent: "#2c3e50"          # optional: wiki browser accent color, light theme
      accent_dark: "#42b983"     # optional: accent color, dark theme
    components:
      - slug: acme-api
        owner: Platform team
        repo: https://github.com/acme/acme-api

It holds no secrets.  Unknown keys are ignored so that a newer file still loads.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

CONFIG_FILE = "manifold.yaml"
SCHEMA_VERSION = 1
DEFAULT_NAME = "Manifold"
DEFAULT_SERVER_NAME = "manifold"
DEFAULT_ACCENT = "#2c3e50"
DEFAULT_ACCENT_DARK = "#42b983"
_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

# A component slug is lowercase ASCII letters and digits, with single dots,
# hyphens or underscores between them, and at most 64 characters.  It is used
# as a directory name, so it never contains a slash or a leading dot.
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_MAX_SLUG = 64


class ConfigError(Exception):
    """manifold.yaml is missing or invalid.  The message says how to fix it."""


@dataclass(frozen=True)
class Component:
    slug: str
    repo: str = ""
    owner: str = ""
    description: str = ""


@dataclass(frozen=True)
class Config:
    version: int
    name: str
    server_name: str
    components: Tuple[Component, ...]
    accent: str = DEFAULT_ACCENT
    accent_dark: str = DEFAULT_ACCENT_DARK

    def slugs(self) -> List[str]:
        return [c.slug for c in self.components]


def valid_slug(slug: object) -> bool:
    """True when ``slug`` is a well-formed component slug."""
    return isinstance(slug, str) and len(slug) <= _MAX_SLUG and bool(_SLUG_RE.match(slug))


def config_path(wiki_root: Path) -> Path:
    return Path(wiki_root) / CONFIG_FILE


def _text(value: object, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, (str, int, float)):
        raise ConfigError("%s: %s must be text" % (CONFIG_FILE, field))
    return str(value)


def load_config(wiki_root: Path) -> Config:
    """Read and validate ``manifold.yaml``.  Raises :class:`ConfigError`."""
    path = config_path(wiki_root)
    if not path.is_file():
        raise ConfigError(
            "%s not found at the instance root. Create it with a version and a components list "
            "(see examples/acme/manifold.yaml)." % CONFIG_FILE
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ConfigError("%s is not valid YAML: %s" % (CONFIG_FILE, exc))
    if not isinstance(data, dict):
        raise ConfigError("%s must be a mapping with a version and a components list" % CONFIG_FILE)

    version = data.get("version")
    if version != SCHEMA_VERSION:
        raise ConfigError(
            "%s: version must be %d, got %r" % (CONFIG_FILE, SCHEMA_VERSION, version)
        )

    raw_components = data.get("components") or []
    if not isinstance(raw_components, list):
        raise ConfigError("%s: components must be a list" % CONFIG_FILE)
    seen = set()
    components = []
    for index, item in enumerate(raw_components):
        if not isinstance(item, dict):
            raise ConfigError("%s: components[%d] must be a mapping with a slug" % (CONFIG_FILE, index))
        slug = item.get("slug")
        if not valid_slug(slug):
            raise ConfigError(
                "%s: components[%d] has an invalid slug %r (lowercase letters, digits and single "
                "dots, hyphens or underscores, at most %d characters)" % (CONFIG_FILE, index, slug, _MAX_SLUG)
            )
        if slug in seen:
            raise ConfigError("%s: component %r is listed twice" % (CONFIG_FILE, slug))
        seen.add(slug)
        components.append(Component(
            slug=slug,
            repo=_text(item.get("repo"), "components[%d].repo" % index),
            owner=_text(item.get("owner"), "components[%d].owner" % index),
            description=_text(item.get("description"), "components[%d].description" % index),
        ))

    brand = data.get("brand") or {}
    if not isinstance(brand, dict):
        raise ConfigError("%s: brand must be a mapping" % CONFIG_FILE)
    colors = {}
    for key, default in (("accent", DEFAULT_ACCENT), ("accent_dark", DEFAULT_ACCENT_DARK)):
        value = _text(brand.get(key), "brand.%s" % key) or default
        if not _COLOR_RE.match(value):
            raise ConfigError("%s: brand.%s must be a color like #2c3e50, got %r" % (CONFIG_FILE, key, value))
        colors[key] = value

    name = _text(data.get("name"), "name") or DEFAULT_NAME
    server_name = _text(data.get("server_name"), "server_name") or DEFAULT_SERVER_NAME
    return Config(version=SCHEMA_VERSION, name=name, server_name=server_name, components=tuple(components),
                  accent=colors["accent"], accent_dark=colors["accent_dark"])


def registered_slugs(wiki_root: Path) -> List[str]:
    """Slugs of the registered components, in file order.  Raises :class:`ConfigError`."""
    return load_config(wiki_root).slugs()


def _entry_lines(component: Component, indent: str) -> List[str]:
    """YAML text for one registry entry.  JSON strings are valid double-quoted YAML."""
    lines = ["%s- slug: %s\n" % (indent, component.slug)]
    for key in ("owner", "repo", "description"):
        value = getattr(component, key)
        if value:
            lines.append("%s  %s: %s\n" % (indent, key, json.dumps(value, ensure_ascii=False)))
    return lines


_BLOCK_KEY = re.compile(r"^components:\s*(#.*)?$")
_EMPTY_FLOW = re.compile(r"^components:\s*\[\s*\]\s*(#.*)?$")
_ITEM = re.compile(r"^(\s*)-(\s|$)")


def add_component(wiki_root: Path, component: Component) -> bool:
    """
    Add ``component`` to the registry.  Returns False if its slug is already there.

    The file is edited as text, so comments and ordering survive.  After the
    edit the file is loaded again; if it does not contain the new slug the
    original text is restored and :class:`ConfigError` is raised.
    """
    if not valid_slug(component.slug):
        raise ConfigError("invalid component slug %r" % (component.slug,))
    path = config_path(wiki_root)
    existing = load_config(wiki_root)  # also proves the file is valid before we touch it
    if component.slug in existing.slugs():
        return False

    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    key_index = next((i for i, l in enumerate(lines) if _BLOCK_KEY.match(l) or _EMPTY_FLOW.match(l)), None)
    if key_index is None and any(l.startswith("components:") for l in lines):
        raise ConfigError(
            "components in %s is written in a form that cannot be edited automatically; "
            "add the entry for %r by hand." % (CONFIG_FILE, component.slug)
        )
    if key_index is None:
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.append("components:\n")
        lines.extend(_entry_lines(component, "  "))
    elif _EMPTY_FLOW.match(lines[key_index]):
        lines[key_index:key_index + 1] = ["components:\n"] + _entry_lines(component, "  ")
    else:
        indent = "  "
        last = key_index  # index of the last line that belongs to the block
        for i in range(key_index + 1, len(lines)):
            line = lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            item = _ITEM.match(line)
            if item or line[0] in " \t":
                if item:
                    indent = item.group(1)
                last = i
                continue
            break  # next top-level key
        lines[last + 1:last + 1] = _entry_lines(component, indent)

    path.write_text("".join(lines), encoding="utf-8")
    try:
        if load_config(wiki_root).slugs() != existing.slugs() + [component.slug]:
            raise ConfigError("the edited file does not list the expected components")
    except ConfigError as exc:
        path.write_text(original, encoding="utf-8")
        raise ConfigError(
            "could not add %r to %s automatically (%s); the file was left as it was. "
            "Add the entry by hand." % (component.slug, CONFIG_FILE, exc)
        )
    return True


_SLUG_LIST_HEADER = "Valid component slugs:"


def sync_schema_slugs(wiki_root: Path) -> Optional[Path]:
    """
    Rewrite the slug list in ``wiki/CLAUDE.md`` from the registry.

    The list is generated: ``manifold.yaml`` is the source and the page only
    mirrors it for the agents that read the schema.  Returns the page path if
    it changed, else None.  Pages without the header are left alone.
    """
    page = Path(wiki_root) / "wiki" / "CLAUDE.md"
    if not page.is_file():
        return None
    lines = page.read_text(encoding="utf-8").splitlines(keepends=True)
    header = next((i for i, l in enumerate(lines) if l.strip() == _SLUG_LIST_HEADER), None)
    if header is None:
        return None
    end = header + 1
    while end < len(lines) and lines[end].strip().startswith("- `"):
        end += 1
    wanted = ["- `%s`\n" % slug for slug in registered_slugs(wiki_root)]
    if lines[header + 1:end] == wanted:
        return None
    lines[header + 1:end] = wanted
    page.write_text("".join(lines), encoding="utf-8")
    return page
