from django import template

register = template.Library()


def attr(instance, attr_name):
    value = getattr(instance, attr_name)
    return '' if value is None else value


def urlc(name_space, name):
    return "{name_space}:{name}".format(name_space=name_space, name=name)


register.filter('attr', attr)
register.filter('urlc', urlc)
