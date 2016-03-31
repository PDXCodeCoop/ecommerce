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


def processStripe(request, customer = None):
    args = {}
    stripe.api_key = settings.STRIPE_SECRET_KEY
    token = request.POST['stripeToken']
    amount = request.POST['cc-amount']
    if customer is None:
        customer = stripe.Customer.create(
            source=token,
            description="New Customer"
        )
    try:
        #Save New customer to user
        if request.user.is_authenticated():
            if not BillingInfo.objects.filter(user=request.user).exists():
                billing = BillingInfo(user=request.user, stripe=customer.id)
                billing.save()
            else:
                request.user.billinginfo.stripe = customer.id
                request.user.billinginfo.save()
        order = processProducts(request, request.session.get('cart', []))
        processEmail(order)
        charge = stripe.Charge.create(
            amount=int(order.stripe_total), # amount in cents, again
            currency="usd",
            customer=customer.id,
        )
        args = {
        'cc_result':"Your card was successfully charged $%.2f" % (order.total),
        'order': order,
        }
    except stripe.error.CardError, e:
        # The card has been declined
        args['cc_result'] = e
    return args

def processEmail(order):
    try:
        d = Context({ 'order': order })
        msg_plain = render_to_string('email/notification.txt', d)
        msg_html = render_to_string('email/notification.html', d)
        send_mail(
            'We have a new order!',
            msg_plain,
            'admin@code.coop',
            ["bjageman@code.coop"],
            html_message=msg_html,
        )
        if order.shipping_email is not None:
            msg_plain = render_to_string('email/order_confirm.txt', d)
            msg_html = render_to_string('email/order_confirm.html', d)
            send_mail(
                'Thanks for the order!',
                msg_plain,
                'admin@code.coop',
                [order.shipping_email],
                html_message=msg_html,
            )
        return True
    except:
        return False

def processProducts(request, cart):
    products = setProducts(request.session.get('cart', []))
    user = request.user
    if request.user.is_authenticated():
        address_text = str(user.shipping.name + " " + user.shipping.address + " " + user.shipping.city + ", " + user.shipping.state + " " + user.shipping.postal_code)
        order = Order(user=user, shipping_address=address_text, shipping_email=user.shipping.email)
    else:
        address_text = str(request.session['shipping']['name'] + " " + request.session['shipping']['address'] + " " + request.session['shipping']['city'] + ", " + request.session['shipping']['state'] + " " + request.session['shipping']['postal_code'])
        order = Order(shipping_address=address_text, shipping_email=request.session['shipping']['email'])
    order.save()
    #Edit the quantity of the products in stock
    for item in products:
        quantity = item['session']['quantity']
        #Verify that the product does not go beyond the stock limit
        if not (item['product'].preorder or item['product'].status() == "unlimited"):
            quantity = item['product'].set_limit(quantity)
        for accessory in item['accessories']:
            if accessory is not None:
                if not (accessory.preorder or accessory.status() == "unlimited"):
                    quantity = accessory.set_limit(quantity)
                if accessory.stock is not None:
                    accessory.stock = accessory.stock - quantity
                accessory.save()
        if item['product'].stock is not None:
            item['product'].stock = item['product'].stock - quantity
        addProductToOrder(order, item['product'], item['accessories'], item['options'], quantity)
        item['product'].save()
    order.save()
    if 'coupon' in request.session:
        coupon = Coupon.objects.get(code=request.session['coupon']['code'])
        #This will be need to be changed once product associations are implemented
        order.coupon = coupon.code + ": " + str(coupon.amount_off)
        order.discount = coupon.amount_off
        coupon.times_redeemed = coupon.times_redeemed + 1
        del request.session['coupon']
        coupon.save()
    order.save()
    del request.session['cart']
    return order

def addProductToOrder(order, product, accessories, options, quantity):
    productText = str(product.pk) + ") " + product.title
    accessory_title = ""
    option_title = ""
    for accessory in accessories:
        accessory_title = accessory.title
        productText = productText + " w/ " + accessory.title
    for option in options:
        option_title = option.title
        productText = productText + "(" + option.title +")"
    productOrder = ProductOrder(
            order=order,
            product_log=productText,
            accessories=accessory_title,
            options=option_title,
            quantity=quantity,
            price=getProductTotal(product, accessories, options)
        )
    productOrder.save()

def charge(request):
    args = {}
    if request.user.is_authenticated():
        args["shipping"] = get_object_or_404(Shipping, user=request.user)
    elif 'shipping' in request.session:
        args["shipping"] = request.session['shipping']
    else:
        return HttpResponseRedirect( reverse('store:checkout') )
    args = processStripe(request)
    return render_to_response('store/order-complete.html', RequestContext(request,args))
