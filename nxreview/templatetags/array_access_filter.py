from django import template
register = template.Library()

@register.filter
def array_access(list, index):
    return list[index]