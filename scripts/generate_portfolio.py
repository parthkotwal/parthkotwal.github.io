#!/usr/bin/env python3
"""Generate the machine-readable portfolio and sitemap from the website HTML."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse


SITE_URL = "https://parthkotwal.github.io/"
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SKIPPED_ELEMENTS = {"script", "style", "svg"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if node.tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def parse_html(path: Path) -> Node:
    parser = TreeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.root


def walk(node: Node) -> Iterable[Node]:
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from walk(child)


def find_first(
    node: Node,
    tag: str | None = None,
    *,
    element_id: str | None = None,
    attr: tuple[str, str] | None = None,
) -> Node | None:
    for candidate in walk(node):
        if tag is not None and candidate.tag != tag:
            continue
        if element_id is not None and candidate.attrs.get("id") != element_id:
            continue
        if attr is not None and candidate.attrs.get(attr[0]) != attr[1]:
            continue
        return candidate
    return None


def find_all(node: Node, tag: str | None = None) -> list[Node]:
    return [candidate for candidate in walk(node) if tag is None or candidate.tag == tag]


def has_class(node: Node, class_name: str) -> bool:
    return class_name in node.attrs.get("class", "").split()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def plain_text(node: Node | str) -> str:
    if isinstance(node, str):
        return node
    if node.tag in SKIPPED_ELEMENTS:
        return ""
    if node.tag == "img":
        return node.attrs.get("alt", "")
    return compact("".join(plain_text(child) for child in node.children))


def markdown_inline(node: Node | str, base_url: str) -> str:
    if isinstance(node, str):
        return node
    if node.tag in SKIPPED_ELEMENTS:
        return ""

    inner = compact("".join(markdown_inline(child, base_url) for child in node.children))
    if node.tag == "a":
        href = node.attrs.get("href", "")
        label = inner or node.attrs.get("aria-label", "")
        if not href or not label:
            return label
        return f"[{label}]({urljoin(base_url, href)})"
    if node.tag in {"strong", "b"} and inner:
        return f"**{inner}**"
    if node.tag in {"em", "i"} and inner:
        return f"*{inner}*"
    if node.tag == "code" and inner:
        return f"`{inner}`"
    if node.tag == "br":
        return "\n"
    if node.tag == "img":
        return node.attrs.get("alt", "")
    return inner


def render_table(table: Node, base_url: str) -> list[str]:
    rows: list[list[str]] = []
    for row in find_all(table, "tr"):
        cells = [
            compact(markdown_inline(cell, base_url)).replace("|", "\\|")
            for cell in row.children
            if isinstance(cell, Node) and cell.tag in {"th", "td"}
        ]
        if cells:
            rows.append(cells)

    if not rows:
        return []
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = [
        "| " + " | ".join(rows[0]) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return lines


def render_project_section(section: Node, base_url: str) -> list[str]:
    heading = find_first(section, "h2")
    if heading is None:
        return []

    lines = [f"### {plain_text(heading)}", ""]
    for child in section.children:
        if isinstance(child, str) or child is heading:
            continue
        if child.tag == "p":
            text = compact(markdown_inline(child, base_url))
            if text:
                lines.extend([text, ""])
        elif child.tag == "blockquote":
            text = compact(markdown_inline(child, base_url))
            if text:
                lines.extend([f"> {text}", ""])
        elif has_class(child, "project-flow"):
            label = child.attrs.get("aria-label", "Process")
            lines.extend([f"**{label}:**", ""])
            for step in child.children:
                if not isinstance(step, Node) or not has_class(step, "project-flow-step"):
                    continue
                parts = [
                    plain_text(part)
                    for part in step.children
                    if isinstance(part, Node) and part.tag in {"span", "strong", "small"}
                ]
                parts = [part for part in parts if part]
                if parts:
                    lines.append("- " + " — ".join(parts))
            lines.append("")
        else:
            table = child if child.tag == "table" else find_first(child, "table")
            if table is not None:
                lines.extend(render_table(table, base_url))
                lines.append("")
    return lines


def canonical_url(document: Node, fallback: str) -> str:
    for link in find_all(document, "link"):
        if "canonical" in link.attrs.get("rel", "").split():
            return link.attrs.get("href", fallback)
    return fallback


def render_project(document: Node, fallback_url: str) -> tuple[str, str]:
    page_url = canonical_url(document, fallback_url)
    main = find_first(document, "main", element_id="project-note")
    if main is None:
        raise ValueError(f"No project-note main element in {fallback_url}")

    article = find_first(main, "article")
    if article is None:
        raise ValueError(f"No article element in {fallback_url}")
    header = next(
        (child for child in article.children if isinstance(child, Node) and child.tag == "header"),
        None,
    )
    if header is None:
        raise ValueError(f"No article header in {fallback_url}")

    title_node = find_first(header, "h1")
    title = plain_text(title_node) if title_node else page_url
    summary_node = find_first(header, "p")
    summary = compact(markdown_inline(summary_node, page_url)) if summary_node else ""

    technologies: list[str] = []
    technology_group = find_first(header, "div", attr=("aria-label", "Technologies used"))
    if technology_group is not None:
        technologies = [plain_text(child) for child in technology_group.children if isinstance(child, Node)]
        technologies = [technology for technology in technologies if technology]

    source_url = ""
    for anchor in find_all(header, "a"):
        href = anchor.attrs.get("href", "")
        if "github.com/" in href:
            source_url = href
            break

    lines = [f"## [{title}]({page_url})", ""]
    if summary:
        lines.extend([summary, ""])
    if technologies:
        lines.extend([f"**Technologies:** {' · '.join(technologies)}", ""])
    if source_url:
        lines.extend([f"**Source:** [GitHub]({source_url})", ""])

    project_copy = next(
        (
            node
            for node in walk(article)
            if node.tag == "div" and has_class(node, "project-copy")
        ),
        None,
    )
    if project_copy is not None:
        for child in project_copy.children:
            if isinstance(child, Node) and child.tag == "section":
                lines.extend(render_project_section(child, page_url))

    return title, "\n".join(lines).rstrip()


def project_documents(root: Path) -> dict[str, tuple[Path, Node]]:
    projects: dict[str, tuple[Path, Node]] = {}
    for path in sorted(root.glob("*/index.html")):
        document = parse_html(path)
        if find_first(document, "main", element_id="project-note") is not None:
            projects[path.parent.name] = (path, document)
    return projects


def project_order(home: Node, projects: dict[str, tuple[Path, Node]]) -> list[str]:
    ordered: list[str] = []
    section = find_first(home, "section", element_id="projects")
    if section is not None:
        for anchor in find_all(section, "a"):
            href = anchor.attrs.get("href", "")
            if not href or href.startswith(("#", "mailto:")):
                continue
            path = urlparse(urljoin(SITE_URL, href)).path.strip("/")
            if path in projects and path not in ordered:
                ordered.append(path)
    ordered.extend(project for project in projects if project not in ordered)
    return ordered


def render_home_context(root: Path, home: Node) -> list[str]:
    hero = next(
        (
            node
            for node in find_all(home, "section")
            if not node.attrs.get("id") and find_first(node, "h1") is not None
        ),
        None,
    )
    name = plain_text(find_first(hero, "h1")) if hero else "Parth Kotwal"
    tagline = plain_text(find_first(hero, "h2")) if hero else ""

    lines = [
        "<!-- Generated by scripts/generate_portfolio.py. Edit the HTML pages or now.json, not this file. -->",
        "",
        f"# {name}",
        "",
    ]
    if tagline:
        lines.extend([f"> {tagline}", ""])
    lines.extend(
        [
            f"**Website:** [{SITE_URL}]({SITE_URL})",
            "",
            "This is the plain-Markdown version of the portfolio, generated from the public website for readers and AI tools.",
            "",
        ]
    )

    about = find_first(home, "section", element_id="about")
    if about is not None:
        heading = find_first(about, "h2")
        lines.extend([f"## {plain_text(heading) if heading else 'About'}", ""])
        intro = find_first(about, "p")
        if intro is not None:
            lines.extend([compact(markdown_inline(intro, SITE_URL)), ""])

        now_path = root / "now.json"
        if now_path.exists():
            now = json.loads(now_path.read_text(encoding="utf-8"))
            current_projects = now.get("projects", [])
            if current_projects:
                lines.extend(["### Building right now", ""])
                for project in current_projects:
                    name_value = compact(str(project.get("name", "")))
                    description = compact(str(project.get("description", "")))
                    if name_value:
                        suffix = f" — {description}" if description else ""
                        lines.append(f"- **{name_value}**{suffix}")
                lines.append("")

        hobby_heading = next(
            (node for node in find_all(about, "h3") if "spare time" in plain_text(node).lower()),
            None,
        )
        hobbies = [
            compact(markdown_inline(node, SITE_URL))
            for node in find_all(about, "span")
            if "text-lg" in node.attrs.get("class", "").split()
        ]
        hobbies = [hobby for hobby in hobbies if hobby]
        if hobbies:
            lines.extend([f"### {plain_text(hobby_heading) if hobby_heading else 'Outside of work'}", ""])
            lines.extend(f"- {hobby}" for hobby in hobbies)
            lines.append("")

    experience = find_first(home, "section", element_id="experience")
    if experience is not None:
        heading = find_first(experience, "h2")
        lines.extend([f"## {plain_text(heading) if heading else 'Experience'}", ""])
        for card in find_all(experience, "li"):
            if not has_class(card, "work-row"):
                continue
            role = find_first(card, "h3")
            if role is not None:
                company = next(
                    (node for node in find_all(card, "p") if has_class(node, "work-company")),
                    None,
                )
                description = next(
                    (node for node in find_all(card, "p") if has_class(node, "work-description")),
                    None,
                )
                date = find_first(card, "time")
                company_text = plain_text(company) if company is not None else ""
                title = f"{plain_text(role)}, {company_text}" if company_text else plain_text(role)
                metadata = [
                    text
                    for text in (
                        plain_text(date) if date is not None else "",
                        plain_text(description) if description is not None else "",
                    )
                    if text
                ]
                suffix = f" — {' — '.join(metadata)}" if metadata else ""
                lines.append(f"- **{title}**{suffix}")
        lines.append("")

    return lines


def render_contacts(home: Node) -> list[str]:
    contact = find_first(home, "section", element_id="contact")
    if contact is None:
        return []
    links: list[str] = []
    for anchor in find_all(contact, "a"):
        href = anchor.attrs.get("href", "")
        label = anchor.attrs.get("aria-label", "") or plain_text(anchor)
        if href and label:
            links.append(f"- [{label}]({href})")
    if not links:
        return []
    return ["## Contact", "", *links, ""]


def build_portfolio(root: Path) -> tuple[str, list[str]]:
    home = parse_html(root / "index.html")
    projects = project_documents(root)
    order = project_order(home, projects)

    lines = render_home_context(root, home)
    lines.extend(["## Projects", ""])

    urls = [SITE_URL]
    for project in order:
        path, document = projects[project]
        fallback_url = urljoin(SITE_URL, f"{project}/")
        _, rendered = render_project(document, fallback_url)
        lines.extend([rendered, ""])
        urls.append(canonical_url(document, fallback_url))

    lines.extend(render_contacts(home))
    portfolio = "\n".join(lines).rstrip() + "\n"
    return portfolio, urls


def build_sitemap(urls: list[str]) -> str:
    all_urls = [*urls, urljoin(SITE_URL, "portfolio.md")]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in all_urls:
        lines.extend(["  <url>", f"    <loc>{url}</loc>", "  </url>"])
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def update_file(path: Path, content: str, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return True
    if check:
        print(f"Out of date: {path.relative_to(path.parent.parent if path.parent.name == 'scripts' else path.parent)}")
        return False
    path.write_text(content, encoding="utf-8")
    print(f"Updated {path.name}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated files are stale")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    portfolio, urls = build_portfolio(root)
    sitemap = build_sitemap(urls)

    results = [
        update_file(root / "portfolio.md", portfolio, check=args.check),
        update_file(root / "sitemap.xml", sitemap, check=args.check),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
