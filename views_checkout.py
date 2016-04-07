from __future__ import division

from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext, Context
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.template.loader import render_to_string

import stripe

from models import *
from django.conf import settings

from views_utils import *

def totalCart(products, discount = None, shipping = None, tax = None):
    total = 0; subtotal = 0
    for product in products:
        subtotal = subtotal + (float(product['price']) * float(product['session']['quantity']))
    #Handling Discounts, Taxes, and Shipping
    total = subtotal
    if discount is not None:
        total = total - discount
    if shipping is not None:
        total = total - shipping
    if tax is not None:
        total = total - tax
    return subtotal, total

def processCoupon(code):
    try:
        code_check = Coupon.objects.get(code=code)
        if code_check.is_expired or code_check.none_left:
            return None
        return code_check
    except Coupon.DoesNotExist:
        return None

def shipping(request):
    if request.method == "POST":
        form = ShippingForm(request.POST)
        if form.is_valid():
            shipping = form.save(commit=False)
            if request.user.is_authenticated():
                shipping.user = request.user
                shipping.email = request.user.email
            shipping.save()
        else:
            return HttpResponseRedirect( reverse('store:index') ) #Report Error Here
        #Not the best way to handle a guest account
        #PLEASE CHANGE SOON
        request.session['shipping'] = {
            'id':shipping.pk,
            'name': shipping.name,
            'address':shipping.address,
            'city':shipping.city,
            'state':shipping.state,
            'postal_code':shipping.postal_code,
            'email':shipping.email,
        }
    return HttpResponseRedirect( reverse('store:checkout') )

def delete_shipping(request):
    if request.user.is_authenticated() and request.user.shipping is not None:
        request.user.shipping.delete()
    if 'shipping' in request.session:
        del request.session['shipping']
    return HttpResponseRedirect( reverse('store:checkout') )

def getShipping(request):
    if request.user.is_authenticated():
        if Shipping.objects.filter(user=request.user).exists():
            return request.user.shipping
        else:
            return None
    elif 'shipping' in request.session:
        return request.session['shipping']
    else:
        return None

### Checkout
def checkout(request):
    args = {}; customer = None
    if 'coupon' in request.session:
        discount = request.session['coupon']['amount'];
    else:
        discount = 0
    tax = 0; shipping = 0;
    if request.method == "POST":
        if 'coupon_code' in request.POST:
            coupon_result = processCoupon(request.POST['coupon_code'])
            if coupon_result is not None and coupon_result.valid == True:
                request.session['coupon'] = {}
                request.session['coupon']['code'] = request.POST['coupon_code']
                discount = float(coupon_result.amount_off)
                request.session['coupon']['amount'] = discount
                args['coupon_result'] = True
            else:
                args['coupon_result'] = False
    products = setProducts(request.session.get('cart', []))
    request.session['subtotal'], request.session['total'] = totalCart(products, discount, tax, shipping)
    shipping = getShipping(request)
    if hasattr(settings, 'STRIPE_PUBLIC_KEY'):
        args['stripe_pub_key'] = settings.STRIPE_PUBLIC_KEY
    if hasattr(settings, 'PAYPAL_MERCHANT_ID'):
        args['paypal_merchant_id'] = settings.PAYPAL_MERCHANT_ID
    args.update({
        'products': products,
        'customer': customer,
        'shipping': shipping,
        'shippingform':ShippingForm(),
})

    return render_to_response('store/checkout.html', RequestContext(request,args))
