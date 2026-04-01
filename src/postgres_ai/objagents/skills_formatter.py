def format_skills(skills: list[dict]) -> str:
    """Format a list of {input, output} skill dicts into a few-shot examples block."""
    if not skills:
        return ""
    lines = ["\n\nFew-shot examples:\n"]
    for skill in skills:
        lines.append(f"Q: {skill['input']}")
        lines.append(f"A:\n{skill['output']}\n")
    return "\n".join(lines)
