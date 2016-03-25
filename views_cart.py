from __future__ import division

from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import stripe
import copy

from models import *
from views_utils import *

#Adds an item to the cart
def addToCart(request):
    cart = request.session.get('cart', [])
    if request.method == "POST":
        if 'item_id' in request.POST:
            product_id = request.POST['item_id']
            product = get_object_or_404(Product, pk = product_id)
            accessory = None
            if product.preorder or product.status() == "unlimited" or int(product.stock) >= 1:
                if getPostValue(request, "accessory") is not None:
                    try:
                        accessory = get_object_or_404(Product, pk = getPostValue(request, "accessory"))
                    except Product.DoesNotExist:
                        return HttpResponseRedirect( reverse('store:checkout') )
                    if not (accessory is not None and accessory.preorder or accessory.status() == "unlimited" or int(accessory.stock) >= 1):
                        return HttpResponseRedirect( reverse('store:checkout') )
                newCartItem = {
                    "product_id": product.pk,
                    "quantity": 1,
                    "accessory": getPostValue(request, "accessory"),
                    "option": getPostValue(request, "option"),
                    }
                if not findDuplicateDictInList(newCartItem, cart, ['quantity']):
                    cart.append(newCartItem)
    request.session['cart'] = cart
    return HttpResponseRedirect( reverse('store:checkout') )

#Changes the quantity in the cart
def changeQuantity(request):
    cart = request.session.get('cart', [])
    if request.method == "POST":
        item_id = int(getPostValue(request, "item_id"))
        item = cart[item_id]
        try:
            product = get_object_or_404(Product, pk = item['product_id'])
            item['quantity'] = product.set_limit(int(getPostValue(request, "quantity")))
            if item['accessory'] is not None:
                accessory = get_object_or_404(Product, pk = item['accessory'])
                item['quantity'] = accessory.set_limit(item['quantity'])
            if item['quantity'] < 0:
                del cart[item_id]
        except Product.DoesNotExist:
            del cart[item_id]
    request.session['cart'] = cart
    return HttpResponseRedirect( reverse('store:checkout') )

def delete(request, product_id):
    cart = request.session.get('cart', [])
    del cart[int(product_id)]
    if len(cart) < 1:
        if 'coupon' in request.session:
            del request.session['coupon']
    request.session['cart'] = cart
    return HttpResponseRedirect( reverse('store:checkout') )
