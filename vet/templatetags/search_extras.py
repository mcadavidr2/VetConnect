from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight(text, query):
    """Simple highlight: wraps occurrences of query in <mark> tags (case-insensitive)."""
    if not query:
        return text or ''
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text or '')
        return mark_safe(highlighted)
    except re.error:
        return text
