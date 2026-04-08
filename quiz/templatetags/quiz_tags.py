from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """获取字典中指定key的值"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None
