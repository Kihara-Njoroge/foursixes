from .models import Cart, CartItem
from django.contrib.auth.signals import user_logged_in

'''
if user is logged in add items to his cart and not to session cart
'''


def get_or_set_cart_session(request):
    if request.user.is_authenticated:
        user = request.user
        user_cart_queryset = user.cart
        if user_cart_queryset.exists():
            cart = user_cart_queryset.first()
        else:
            cart = Cart(user=user)
            cart.save()
        return cart

    cart_id = request.session.get('cart_id', None)

    if cart_id is None:
        cart = Cart()
        cart.save()
        request.session['cart_id'] = cart.id

    else:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart()
            cart.save()
            request.session['cart_id'] = cart.id

    # if request.user.is_authenticated and cart.user is None:
    #     cart.user = request.user
    #     cart.save()
    return cart


'''
upon login add session's cart items to user's cart items and delete session's cart
if user's cart does not exist then assign user to session's cart and clear cart_id form session
'''

# below funtion to be called only upon login


def set_user_cart(sender, user, request, **kwargs):
    if request.user.is_authenticated:
        session_cart_id = request.session.get('cart_id', None)
        if session_cart_id is None:
            session_cart = None
        else:
            try:
                session_cart = Cart.objects.get(id=session_cart_id, user=None)
            except Cart.DoesNotExist:
                session_cart = None
        # user = request.user
        user_cart_queryset = user.cart
        if user_cart_queryset.exists():
            user_cart = user_cart_queryset.first()
            if session_cart is None:
                return
            elif session_cart.items.exists():
                # add or update items form session_cart to user_cart
                session_cart_items = session_cart.items.all()
                for item in session_cart_items:
                    item_filter = CartItem.objects.filter(
                        cart=user_cart, product=item.product, size=item.size)
                    if item_filter.exists():
                        user_cart_item = item_filter.first()
                        user_cart_item.quant = item.quant
                        user_cart_item.save()  # maybe time consuming to save individual objects. ToDo: Bulksave
                    else:
                        item.cart = user_cart
                        item.save()
            # now delete the session cart as it is stale
            # this will have cascading effect and delete its cart items
            session_cart.delete()
            user_cart.set_total_price_and_quant()
            user_cart.save()
            # delete corresponding cart_id form session storage if it existed
            if session_cart_id:
                del request.session['cart_id']
        else:
            if session_cart is None:
                user_cart = Cart.objects.create(user=user)
                user_cart.save()
            else:
                session_cart.user = user
                session_cart.save()
                if session_cart_id:
                    del request.session['cart_id']


user_logged_in.connect(set_user_cart)
