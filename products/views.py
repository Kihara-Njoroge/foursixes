from django.core import paginator
from django.shortcuts import render, get_object_or_404, Http404, HttpResponse, redirect
from django.forms.models import model_to_dict
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from django.core import serializers
from django.http import JsonResponse, HttpResponseBadRequest
from accounts.forms import AddressCreationForm
import json
from . models import Product, Wishlist, Cart, CartItem, Order, OrderItem
from .utils import *


def calculateshipping(total_price):
    shipping_cost = 0
    amount_payable = total_price + shipping_cost
    return amount_payable, shipping_cost


def index(request):
    pdlist = Product.objects.all().order_by('?')
    # filtering
    pdlist = apply_filters(pdlist,request)
    paginator = Paginator(pdlist, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Infinity Fashion | ' + "ALL"
    return render(request, 'pdlist.html', context={'pdlist': pdlist, 'page_obj':page_obj, 'title': title})


def apply_filters(pdlist, request):
    categories = request.GET.getlist('category')
    brands = request.GET.getlist('brand')
    price_low = request.GET.get('price_down')
    price_high = request.GET.get('price_up')
    if categories:
        pdlist = pdlist.filter(category__in=categories)
    if brands:
        pdlist = pdlist.filter(brand__in=brands)
    if price_low and price_high:
        pdlist = pdlist.filter(price__gte=price_low, price__lte=price_high)
    return pdlist


def shopgender(request, type):
    type = type.lower()
    if type == 'clothes':
        pdlist = Product.objects.filter(type='clothes').order_by('?')
    elif type == 'watches':
        pdlist = Product.objects.filter(type='watches').order_by('?')
    elif type == 'shoes':
        pdlist = Product.objects.filter(type='shoes').order_by('?')
    elif type == 'lingerie':
        pdlist = Product.objects.filter(type='lingerie').order_by('?')
    elif type == 'bags':
        pdlist = Product.objects.filter(type='bags').order_by('?')
    else:
        raise Http404("Page not found :(")

    # filtering
    pdlist = apply_filters(pdlist,request)
    paginator = Paginator(pdlist,20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Infinity Fashion | ' + type
    return render(request, 'pdlist.html', context={'pdlist': pdlist, 'page_obj':page_obj, 'title': title})


def search(request):
    if request.method == 'GET':
        # q = search term
        query = request.GET.get('q','')
        query = query.lower().strip()
        pdlist = Product.objects.all()
        fltr = Product.objects.filter(Q(name__icontains=query) | Q(type__icontains=query))
        pdlist = pdlist & fltr
        pdlist = apply_filters(pdlist, request) 
        paginator = Paginator(pdlist,20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        title = 'Search'
        return render(request, 'pdlist.html', context={'pdlist': pdlist, 'page_obj':page_obj, 'title': title})



def product_detail(request, uqid):
    try:
        product = get_object_or_404(Product, uqid=uqid)
    except:
        raise Http404("No Page exists at this url")
    is_wishlisted = False
    if request.user.is_authenticated:
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            is_wishlisted = True

    title = str(product)
    context = {'title': title, 'product': product,
               'is_wishlisted': is_wishlisted}
    return render(request, 'pdp.html', context=context)


def cart(request):
    cart = get_or_set_cart_session(request)
    cart_items = cart.items.all()
    # shipping_cost = 0
    # # cart.total_price excludes shipping cost
    # if cart.total_price < 800:
    #     shipping_cost = 50
    total_payable_price, shipping_cost = calculateshipping(cart.total_price)
    context = {'cart': cart, 'cart_items': cart_items,
               'shipping_cost': shipping_cost, 'payable_amount': total_payable_price}
    return render(request, 'cart.html', context=context)
    # return JsonResponse({'action': 'done'}, status=400)


@login_required(login_url='accounts:login')
def wishlist(request):
    # items = json.loads(serializers.serialize("json", request.user.wlist.all()))
    # print(items, type(items))
    items_pk = request.user.wlist.all().values_list('product', flat=True)
    items = Product.objects.filter(id__in=items_pk)

    return render(request, 'wishlist.html', context={'pdlist': items})

@login_required(login_url='accounts:login')
def wishlist_add_remove_product(request):
    is_success = False
    status = 400
    data = {'is_success': is_success}
    if request.user.is_authenticated:
        if request.is_ajax and request.method == "POST":
            postdata = json.loads(request.body)
            uqid = postdata.get('uqid', '')
            action = 'add'
            if uqid:
                try:
                    prod = Product.objects.get(uqid=uqid)
                except:
                    prod = None
                if prod:
                    status = 200
                    is_success = True
                    wl, created = Wishlist.objects.get_or_create(
                        user=request.user, product=prod)
                    if not created:
                        action = 'remove'
                        wl.delete()
                    data['action'] = action
                    data['is_success'] = is_success
                    return JsonResponse(data, status=status)

    return JsonResponse(data, status=status)


def addtocart(request):
    if request.method == 'POST' and request.is_ajax:
        cart = get_or_set_cart_session(request)
        postdata = json.loads(request.body)
        uqid = postdata.get('uqid', None)
        size = postdata.get('size', None)
        quant = postdata.get('quant', None)
        if uqid and size and quant:
            try:
                quant = int(quant)

                if quant < 1:
                    return HttpResponseBadRequest('Minimum quantity is one.')
                product = Product.objects.get(uqid=uqid)
            except:
                return HttpResponseBadRequest()
            item_filter = cart.items.filter(product=product, size=size)
            # if given product and size is already in cart, update its quantity
            if item_filter.exists():
                cart_item = item_filter.first()
                diff = (cart_item.quant - quant)
                cart.total_quant -= diff
                cart.total_price -= (diff * product.price)
                cart.save()
                cart_item.quant = quant
                cart_item.save()
            # add new product to cart
            else:
                cart_item = CartItem.objects.create(
                    cart=cart, product=product, size=size, quant=quant)
                cart.total_quant += quant
                cart.total_price += (quant * product.price)
                cart.save()
            # return HttpResponseBadRequest()
            cart_total_quant = cart.total_quant
            return JsonResponse({'action': 'success', 'total_quant':cart_total_quant}, status=200)
        else:
            return HttpResponseBadRequest()
    return HttpResponseBadRequest()


def removefromcart(request):
    if request.method == 'POST' and request.is_ajax:
        cart = get_or_set_cart_session(request)
        postdata = json.loads(request.body)
        cart_item_id = postdata.get('citemid', None)
        try:
            cart_item = CartItem.objects.get(cart=cart, id=cart_item_id)
        except:
            return HttpResponseBadRequest()
        cart.total_quant -= cart_item.quant
        cart.total_price -= (cart_item.quant * cart_item.product.price)
        cart_item.delete()
        cart.save()
        response = {'total_price': cart.total_price,
                    'total_quant': cart.total_quant, 'action': 'success'}
        return JsonResponse(response, status=200)
    return HttpResponseBadRequest()


def updatequant(request):
    if request.method == 'POST' and request.is_ajax:
        cart = get_or_set_cart_session(request)
        postdata = json.loads(request.body)
        cart_item_id = postdata.get('citemid', None)
        quant = postdata.get('quant', None)
        try:
            quant = int(quant)
            if quant > 5:
                return HttpResponseBadRequest('Quantity cannot be more than 5.')
            elif quant < 1:
                return HttpResponseBadRequest('Minimum quantity is one.')
            cart_item = CartItem.objects.get(cart=cart, id=cart_item_id)
        except:
            return HttpResponseBadRequest()
        diff = (cart_item.quant - quant)
        cart.total_quant -= diff
        cart.total_price -= (diff * cart_item.product.price)
        cart.save()
        cart_item.quant = quant
        cart_item.save()
        response = {'total_price': cart.total_price,
                    'total_quant': cart.total_quant, 'action': 'success'}
        return JsonResponse(response, status=200)
    return HttpResponseBadRequest()



def testurl(request):
    # print(get_current_site(request))
    # return render(request, 'paymentsuccess.html')
    return HttpResponse("DONE")


def addresspage(request):
    if request.method == "GET":
        cart = get_or_set_cart_session(request)
        if not cart.items.exists():
            return redirect('products:cart')
        cart_items = cart.items.all()
        form = AddressCreationForm()
        total_payable_price, shipping_cost = calculateshipping(cart.total_price)
        context = {'cart': cart, 'cart_items': cart_items,
               'shipping_cost': shipping_cost, 'payable_amount': total_payable_price, 'form':form}
        return render(request, 'address.html', context=context)
        
def checkout(request):
    template = get_template('checkout.html')
    order_item_list = []
    order_item_dict = {}
    if request.method == "POST":
        user = request.user
        cart = get_or_set_cart_session(request)
        cart_items = cart.items.all()
        if cart_items.exists():
            # order's total prices includes shipping
            address_form = AddressCreationForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.save()
            else:
                return redirect('products:cart')
            order_total_price, shipping_cost = calculateshipping(
                cart.total_price)
            order = Order.objects.create(total_price=order_total_price, total_quant=cart.total_quant, shipping_cost=shipping_cost, shipping_address=address)
            # copy cart items to order items
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order, product=item.product, size=item.size, quant=item.quant, item_price=item.product.price)
        else:
            return redirect('products:cart')
        


        order.save()
        context = {}

        # bag_total is price without shipping
        context={'bag_total': cart.total_price,'shipping_cost':shipping_cost,'address':address,
                'order':order, 'order_item':order_item, 'cart_items':cart_items}

        html = template.render(context)

        pdf = render_to_pdf('order_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "order%s.pdf" % (
                "12341231")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


@login_required(login_url='accounts:login')
def myOrders(request):
  user = request.user
  orderitems = OrderItem.objects.all()
  orders = Order.objects.all().filter(user=user)

  context = {'order':orders}

  return render(request, 'orders.html', context)