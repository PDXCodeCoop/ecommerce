from __future__ import division

from django.shortcuts import render_to_response,  get_object_or_404, redirect
from django.template.context import RequestContext

import stripe
from models import *
from views_browse import *
from views_cart import *
from views_checkout import *

# The Store Homepage
def index(request):
    products = Product.objects.all()[:6]
    features = Feature.objects.all()
    categories = Category.objects.all()[:10]
    args = {
        'products': products,
        'features': features,
        'categories': categories,
    }
    return render_to_response('store/index.html', RequestContext(request,args))
