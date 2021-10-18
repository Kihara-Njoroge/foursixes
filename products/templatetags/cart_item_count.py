from django import template
from products.utils import get_or_set_cart_session

register = template.Library()


@register.simple_tag
def item_count(request):
    cart = get_or_set_cart_session(request)
    return cart.items.count()
