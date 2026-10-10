"""Markdown and HTML renderers for parsed candidate DSL models."""
from html import escape


def _items(values: list[str] | tuple[str, ...]) -> str:
    return ", ".join(escape(str(value)) for value in values) if values else "—"


def to_markdown(model: object) -> str:
    """Render a parsed candidate profile as a compact Markdown summary."""
    lines = [f"# Candidate: {model.name}", ""]

    contact = getattr(model, "contact", None)
    if contact:
        lines.extend(("## Contact", ""))
        for label, field in (("Emails", "emails"), ("Phones", "phones"), ("URLs", "urls")):
            values = getattr(contact, field, [])
            if values:
                lines.append(f"- **{label}:** {_items(values)}")
        lines.append("")

    experience = getattr(model, "experience", None)
    if experience:
        lines.extend(("## Experience", ""))
        if experience.years is not None:
            lines.append(f"- **Years:** {experience.years}")
        if experience.periods:
            lines.append(f"- **Periods:** {_items(experience.periods)}")
        lines.append("")

    education = getattr(model, "education", None)
    if education and education.entries:
        lines.extend(("## Education", ""))
        for entry in education.entries:
            text = entry.degree
            if entry.institution:
                text += f" at {entry.institution}"
            lines.append(f"- {text}")
        lines.append("")

    lines.extend(("## Skills", ""))
    if model.skills.groups:
        for group in model.skills.groups:
            lines.append(f"- **{group.category}:** {', '.join(group.skills)}")
    else:
        lines.append("- None")
    lines.append("")

    lines.extend(("## Profile classification", ""))
    if model.classification.results:
        for result in model.classification.results:
            lines.append(f"- **{result.profile}: {result.verdict}**")
            if result.sequence:
                lines.append(f"  - Sequence: {', '.join(result.sequence)}")
            if result.missing:
                lines.append(f"  - Missing: {_items(result.missing)}")
    else:
        lines.append("- No profile results")
    return "\n".join(lines).rstrip() + "\n"


def to_html(model: object) -> str:
    """Render a compact candidate card, escaping all model-provided text."""
    esc = lambda value: escape(str(value), quote=True)
    parts = [
        '<article class="candidate-card">',
        f"<h2>{esc(model.name)}</h2>",
    ]

    contact = getattr(model, "contact", None)
    if contact:
        items = []
        for label, field in (("Emails", "emails"), ("Phones", "phones"), ("URLs", "urls")):
            values = getattr(contact, field, [])
            if values:
                items.append(f"<li><strong>{label}:</strong> {_items(values)}</li>")
        if items:
            parts.extend(("<h3>Contact</h3><ul>", *items, "</ul>"))

    experience = getattr(model, "experience", None)
    if experience:
        values = []
        if experience.years is not None:
            values.append(f"{esc(experience.years)} years")
        values.extend(esc(value) for value in experience.periods)
        if values:
            parts.extend(("<h3>Experience</h3>", f"<p>{' · '.join(values)}</p>"))

    education = getattr(model, "education", None)
    if education and education.entries:
        parts.append("<h3>Education</h3><ul>")
        for entry in education.entries:
            text = esc(entry.degree)
            if entry.institution:
                text += f" at {esc(entry.institution)}"
            parts.append(f"<li>{text}</li>")
        parts.append("</ul>")

    parts.append("<h3>Skills</h3>")
    if model.skills.groups:
        parts.append("<ul>")
        for group in model.skills.groups:
            skills = ", ".join(esc(skill) for skill in group.skills)
            parts.append(f"<li><strong>{esc(group.category)}:</strong> {skills}</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>None</p>")

    parts.append("<h3>Profile classification</h3>")
    if model.classification.results:
        parts.append('<ul class="verdicts">')
        for result in model.classification.results:
            verdict = str(result.verdict)
            badge_class = "accepted" if verdict == "ACCEPTED" else "rejected"
            parts.append(
                f'<li><strong>{esc(result.profile)}</strong> '
                f'<span class="badge {badge_class}">{esc(verdict)}</span>'
            )
            if result.sequence:
                parts.append(f"<p>Sequence: {_items(result.sequence)}</p>")
            if result.missing:
                parts.append(f"<p>Missing: {_items(result.missing)}</p>")
            parts.append("</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>No profile results</p>")

    parts.append("</article>")
    body = "\n".join(parts)
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\"><style>"
        "body{font-family:system-ui,sans-serif;color:#172033;margin:0;padding:12px}"
        ".candidate-card{border:1px solid #d8deea;border-radius:12px;padding:18px;max-width:760px}"
        "h2{margin:0 0 12px}h3{font-size:1rem;margin:18px 0 6px}"
        "ul{padding-left:22px}li{margin:5px 0}.badge{border-radius:999px;padding:3px 9px;"
        "font-size:.78rem;font-weight:700}.accepted{background:#dcfce7;color:#166534}"
        ".rejected{background:#fee2e2;color:#991b1b}</style></head><body>"
        f"{body}</body></html>"
    )
