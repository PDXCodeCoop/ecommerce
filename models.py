from __future__ import unicode_literals
from datetime import date

from django.db import models
from django import forms
from easy_thumbnails.fields import ThumbnailerImageField
from django.contrib.auth.models import User

from models_products import *
from models_shipping import *

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
