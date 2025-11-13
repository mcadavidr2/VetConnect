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


@register.filter
def star_rating(value, max_stars=5):
    """Render a simple star-based rating using ★ and ☆ characters."""
    try:
        rating = float(value or 0)
    except (TypeError, ValueError):
        rating = 0

    rating = max(0, min(rating, max_stars))
    filled = int(round(rating))
    empty = max_stars - filled
    stars = '★' * filled + '☆' * empty
    return mark_safe(stars)
