from django import template

register = template.Library()


@register.filter
def inr(value, suffix=''):
    """Format a number as Indian currency shorthand: 5Cr, 50L, 1.5Cr, 25L etc."""
    if value is None:
        return ''
    n = float(value)
    if n >= 1e7:
        v = n / 1e7
        s = f'{v:.2f}'.rstrip('0').rstrip('.')
        return f'₹{s}Cr{suffix}'
    if n >= 1e5:
        v = n / 1e5
        s = f'{v:.1f}'.rstrip('0').rstrip('.')
        return f'₹{s}L{suffix}'
    return f'₹{int(n):,}{suffix}'


@register.filter
def inr_acre(value):
    return inr(value, '/ac')


@register.filter
def inr_sqft(value):
    return inr(value, '/sqft')


@register.filter
def floatstrip(value, places=2):
    """Format decimal, stripping trailing zeros: 10.0000 → 10, 5.5000 → 5.5"""
    if value is None:
        return ''
    try:
        fmt = f'{float(value):.{int(places)}f}'
        return fmt.rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return value
