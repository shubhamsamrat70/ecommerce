from django import template

register = template.Library()

@register.filter
def percentage(price, discount_price):
    if price and discount_price:
        return ((price - discount_price) / price) * 100
    return 0