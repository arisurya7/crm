from django import template
register = template.Library()

@register.filter
def devide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None