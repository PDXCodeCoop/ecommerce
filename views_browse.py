from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import *

### Store browsing
def listing(request):
    product_list = Product.objects.filter(listed=True)
    paginator = Paginator(product_list, 6)

    page = request.GET.get('page')
    #Pagination Code
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    args = {
        'products':products,
    }
    return render_to_response('store/shop.html', RequestContext(request,args))

def listing_category(request, category):
    category_id = get_object_or_404(Category, slug=category)
    products = Product.objects.filter(category=category_id, listed=True)
    args = {
        'products':products,
    }
    return render_to_response('store/shop.html', RequestContext(request,args))

def product_detail(request, pid):
    args = {}
    product = get_object_or_404(Product, pk=pid)
    optioncategories = OptionCategory.objects.filter(product=product)
    related_products = Product.objects.filter(listed=True)[:4]
    accessories_form = AccessoriesForm(); options_form = OptionsForm()
    args = {
        'product':product,
        'optioncategories': optioncategories,
        'related_products':related_products,
        'accessories_form':accessories_form,
        'options_form':options_form,
    }
    return render_to_response('store/product-details.html', RequestContext(request,args))
