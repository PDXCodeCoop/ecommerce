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
        charge = stripe.Charge.create(
            amount=int(amount), # amount in cents, again
            currency="usd",
            customer=customer.id,
        )
        args['cc_result'] = "Your card was successfully charged $" + str(float(amount) /100)
        #Save New customer to user
        if request.user.is_authenticated():
            if not BillingInfo.objects.filter(user=request.user).exists():
                billing = BillingInfo(user=request.user, stripe=customer.id)
                billing.save()
            else:
                request.user.billinginfo.stripe = customer.id
                request.user.billinginfo.save()
        order = processProducts(request, request.session.get('cart', {}))
        try:
            processEmail(order)
        except:
            #Set a method to handle errors
            pass
    except stripe.error.CardError, e:
        # The card has been declined
        args['cc_result'] = e
    return args

def processEmail(order):
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

def processProducts(request, cart):
    cart_list = []
    for key in cart:
        cart_list.append(key)
    products = Product.objects.filter(pk__in = cart_list)
    user = request.user
    if request.user.is_authenticated():
        address_text = str(user.shipping.name + " " + user.shipping.address + " " + user.shipping.city + ", " + user.shipping.state + " " + user.shipping.postal_code)
        order = Order(user=user, shipping_address=address_text, shipping_email=user.shipping.email)
    else:
        address_text = str(request.session['shipping']['name'] + " " + request.session['shipping']['address'] + " " + request.session['shipping']['city'] + ", " + request.session['shipping']['state'] + " " + request.session['shipping']['postal_code'])
        order = Order(shipping_address=address_text, shipping_email=request.session['shipping']['email'])
    order.save()
    #Edit the quantity of the products in stock
    for product in products:
        quantity = int(cart[str(product.pk)])
        if product.status() != "unlimited":
            if (not product.preorder) and quantity > product.stock:
                quantity = product.stock
            product.stock = product.stock - quantity
        addProductToOrder(order, product, quantity)
        product.save()
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

def addProductToOrder(order, product, quantity):
    productText = str(product.pk) + ") " + product.title
    productOrder = ProductOrder(order=order, product_log=productText, quantity=quantity, price=product.total())
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

def totalCart(products, cart, discount = None, shipping = None, tax = None):
    total = 0; subtotal = 0
    for product in products:
        subtotal = subtotal + (cart[str(product.pk)]['quantity'] * int(product.total()))
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
    cart = request.session.get('cart', {})
    cart_list = []
    for key in cart:
        cart_list.append(key)
    products = Product.objects.filter(pk__in = cart_list)
    request.session['subtotal'], request.session['total'] = totalCart(products, cart, discount, tax, shipping)
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
