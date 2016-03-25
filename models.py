from __future__ import unicode_literals
from datetime import date

from django.db import models
from django import forms
from easy_thumbnails.fields import ThumbnailerImageField
from django.contrib.auth.models import User

import json
import urllib
from urlparse import urlparse
from decimal import Decimal

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    def __unicode__(self):
        return self.title

class OptionCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    def __unicode__(self):
        return self.title

class Option(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock = models.IntegerField(null=True, blank=True)
    preorder = models.BooleanField(default = False)
    category = models.ForeignKey(OptionCategory, blank=True, null=True)
    def __unicode__(self):
        return "%s: %s" % (self.category, self.title)

class Accessory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock = models.IntegerField(null=True, blank=True)
    preorder = models.BooleanField(default = False)
    def __unicode__(self):
        return "%s" % (self.title)
    def total(self):
        return (self.price - self.discount) - (self.price * self.percent_off/100)
    def set_limit(self, quantity):
        quantity = int(quantity)
        if self.purchase_limit is not None and quantity > self.purchase_limit:
            quantity = self.purchase_limit
        if self.stock is not None and quantity > self.stock:
            quantity = self.stock
        return quantity
    def status(self):
        if self.stock is None: return "unlimited"
        if self.stock > 0: return "instock"
        if self.stock <= 0:
            if self.preorder: return "preorder"
            else: return "outofstock"

# Create your models here.
class Product(models.Model):
    mainimage = ThumbnailerImageField(upload_to='products', blank=True)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    accessories = models.ManyToManyField('self', blank=True)
    options = models.ManyToManyField(OptionCategory, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    percent_off = models.IntegerField(default=0)
    category = models.ForeignKey(Category, blank=True, null=True)
    purchase_limit = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    preorder = models.BooleanField(default = False)
    featured = models.BooleanField(default = False)
    listed = models.BooleanField(default = False)
    def total(self):
        return (self.price - self.discount) - (self.price * self.percent_off/100)
    def set_limit(self, quantity):
        quantity = int(quantity)
        if self.purchase_limit is not None and quantity > self.purchase_limit:
            quantity = self.purchase_limit
        if self.stock is not None and quantity > self.stock:
            quantity = self.stock
        return quantity
    def status(self):
        if self.stock is None: return "unlimited"
        if self.stock > 0: return "instock"
        if self.stock <= 0:
            if self.preorder: return "preorder"
            else: return "outofstock"
    def __unicode__(self):
        return "%s) %s" % (self.pk, self.title)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images')
    image = ThumbnailerImageField(upload_to='products', blank=True)

class Feature(models.Model):
    photo = ThumbnailerImageField(upload_to='features', blank=True)
    header = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    product = models.ForeignKey(Product, blank=True, null=True)
    def __unicode__(self):
        return self.header

class Shipping(models.Model):
    user = models.OneToOneField(User, null=True)
    email = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100)
    lat = models.DecimalField(max_digits=18, decimal_places=10, null=True)
    lng = models.DecimalField(max_digits=18, decimal_places=10, null=True)
    def __unicode__(self):
        return "%s %s, %s %s" % (self.address, self.city, self.state, self.postal_code)
    def save(self):
        if not self.lat or not self.lng:
            self.lat, self.lng = self.geocode(self.address)
        if self.name is None:
            self.name = str(self.user.first_name + " " + self.user.last_name)
        super(Shipping, self).save()
    def geocode(self, address):
        address = urllib.quote_plus(address)
        maps_api_url = "?".join([
            "http://maps.googleapis.com/maps/api/geocode/json",
            urllib.urlencode({"address":address, "sensor":False})
        ])
        response = urllib.urlopen(maps_api_url)
        data = json.loads(response.read().decode('utf8'))

        if data['status'] == 'OK':
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            return Decimal(lat), Decimal(lng)

class ShippingForm(forms.ModelForm):
    name = forms.CharField(required=False)
    class Meta:
        model = Shipping
        exclude = ('user','lat','lng', 'country')

class BillingInfo(models.Model):
    user = models.OneToOneField(User, null=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    stripe = models.CharField(max_length=50, null=True, blank=True)
    paypal = models.CharField(max_length=50, null=True, blank=True)
    def __unicode__(self):
        return "%s %s" % (self.user, self.address)

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    #valid_products = models.ManyToManyField(Product)
    amount_off = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    currency = models.CharField(default="USD", max_length=50)
    expires = models.DateField(blank=True, null=True)
    valid = models.BooleanField(default=True)
    max_redemptions = models.IntegerField(blank=True, null=True)
    times_redeemed = models.IntegerField(default=0)
    @property
    def is_expired(self):
        if self.expires is not None and date.today() > self.expires:
            return True
        return False
    @property
    def none_left(self):
        if self.max_redemptions is not None and self.times_redeemed >= self.max_redemptions:
            return True
        return False
    def __unicode__(self):
        return "%s - %s (%s/%s)" % (self.code, self.amount_off, self.times_redeemed, self.max_redemptions)

class Order(models.Model):
    class Meta:
        ordering = ['-created']
    user = models.ForeignKey(User, null=True)
    shipping_address =  models.CharField(max_length=500, null=True, blank=True)
    shipping_email =  models.CharField(max_length=100, null=True, blank=True)
    shipped_status = models.BooleanField(default=False)
    delivered_status = models.BooleanField(default=False)
    tracking = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    coupon = models.CharField(max_length=50, null=True, blank=True)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    @property
    def subtotal(self):
        subtotal = 0
        for productorder in self.productorder_set.all():
            subtotal = subtotal + productorder.total()
        return subtotal
    @property
    def total(self):
        subtotal = self.subtotal
        total = subtotal + self.shipping_cost + self.tax - self.discount
        return total
    def __unicode__(self):
        return "Order ID #%s - %s" % (self.pk, self.user)

class ProductOrder(models.Model):
    order = models.ForeignKey(Order)
    #product = models.ForeignKey(Product)
    product_log = models.CharField(max_length=500, null=True, blank=True)
    accessories = models.CharField(max_length=500, null=True, blank=True)
    options = models.CharField(max_length=500, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    def total(self):
        return self.price * self.quantity
    def __unicode__(self):
        return "Order ID #%s - %s" % (self.order.pk, self.product_log)
