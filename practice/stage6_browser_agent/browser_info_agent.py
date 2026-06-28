from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


@dataclass(frozen=True)
class Link:
    text: str
    href: str


@dataclass(frozen=True)
class PageSummary:
    title: str
    headings: list[str]
    links: list[Link]
    text_preview: str
    action_log: list[str]


class PageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self.headings: list[str] = []
        self.links: list[Link] = []
        self.text_parts: list[str] = []
        self._tag_stack: list[str] = []
        self._active_href: str | None = None
        self._active_link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        if tag == "a":
            attrs_dict = dict(attrs)
            self._active_href = attrs_dict.get("href") or ""
            self._active_link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._active_href is not None:
            text = " ".join("".join(self._active_link_text).split())
            self.links.append(Link(text or self._active_href, urljoin(self.base_url, self._active_href)))
            self._active_href = None
            self._active_link_text = []
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        current = self._tag_stack[-1] if self._tag_stack else ""
        if current == "title":
            self.title += text
        if current in {"h1", "h2", "h3"}:
            self.headings.append(text)
        if self._active_href is not None:
            self._active_link_text.append(text)
        if current not in {"script", "style"}:
            self.text_parts.append(text)


class LocalPageAgent:
    def inspect(self, path: Path) -> PageSummary:
        action_log = [f"open:{path}"]
        if not path.exists():
            action_log.append("error:file_not_found")
            return PageSummary("", [], [], "", action_log)
        html = path.read_text(encoding="utf-8")
        action_log.append("read_html")
        parser = PageParser(path.as_uri())
        parser.feed(html)
        action_log.append("parse_dom")
        preview = " ".join(parser.text_parts)[:240]
        action_log.append("summarize")
        return PageSummary(parser.title, parser.headings, parser.links, preview, action_log)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a local HTML page like a tiny browser agent.")
    parser.add_argument("path")
    args = parser.parse_args()
    result = LocalPageAgent().inspect(Path(args.path).resolve())
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

