from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext

from models import *

### Store browsing
def listing(request):
    products = Product.objects.all()
    args = {
        'products':products,
    }
    return render_to_response('store/shop.html', RequestContext(request,args))

def listing_category(request, category):
    category_id = get_object_or_404(Category, slug=category)
    products = Product.objects.filter(category=category_id)
    args = {
        'products':products,
    }
    return render_to_response('store/shop.html', RequestContext(request,args))

def products(request):
    args = {}
    return render_to_response('store/product-details.html', RequestContext(request,args))

def product_detail(request, pid):
    args = {}
    product = get_object_or_404(Product, pk=pid)
    optioncategories = OptionCategory.objects.filter(product=product)
    accessories = Accessory.objects.filter(product=product)
    related_products = Product.objects.all()[:4]
    args = {
        'product':product,
        'accessories': accessories,
        'optioncategories': optioncategories,
        'related_products':related_products,
    }
    return render_to_response('store/product-details.html', RequestContext(request,args))
