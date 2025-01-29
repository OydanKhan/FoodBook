from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Fetches the value for a given key from the given dictionary"""
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    """Subtracts arg from value"""
    return value - arg