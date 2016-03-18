from __future__ import division

from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import stripe

from models import *

def changeQuantity(request):
    cart = request.session.get('cart', {})
    if request.method == "POST":
        if 'item_id' in request.POST:
            product_id = request.POST['item_id']
            product = get_object_or_404(Product, pk = product_id)
            if 'add_quantity' in request.POST:
                add_quantity = int(request.POST['add_quantity'])
                try:
                    cart[product_id] = int(cart[product_id]) + add_quantity
                except KeyError:
                    cart[product_id] = add_quantity
            if 'change' in request.POST:
                cart[product_id] = request.POST['change']
                request.session['output'] = cart
            #Verify that the user is not taking too much stock
            if not (product.preorder or product.status() == "unlimited"):
                cart[product_id] = product.set_limit(cart[product_id])
            if int(cart[product_id]) < 1:
                del cart[product_id]
    request.session['cart'] = cart
    return HttpResponseRedirect( reverse('store:checkout') )

def delete(request, product_id):
    cart = request.session.get('cart', {})
    del cart[product_id]
    if len(cart) < 1:
        if 'coupon' in request.session:
            del request.session['coupon']
    request.session['cart'] = cart
    return HttpResponseRedirect( reverse('store:checkout') )
