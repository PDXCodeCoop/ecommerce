from django.conf.urls import patterns, url

from . import views

urlpatterns = [
       url('^$', views.index, name='index'),
       url('^checkout$', views.checkout, name='checkout'),
       url('^checkout/delete/([0-9]+)$', views.delete, name='cartdelete'),
       url('^cart/change$', views.changeQuantity, name='cartchange'),
       #url('^checkout/change/(?P<product_id>-?\d+)/(?P<quantity>-?\d+)$', views.changeQuantity, name='cartchange'),
       url('^shipping$', views.shipping, name='shipping'),
       url('^shipping/delete', views.delete_shipping, name='delete_shipping'),
       url('^charge/', views.charge, name='charge'),
       url('^products$', views.listing, name='products'),
       url('^products/cat/(?P<category>[\w-]+)$', views.listing_category, name='productscat'),
       url('^products/([0-9]+)$', views.product_detail, name='products'),
       ]
