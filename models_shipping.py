from django.db import models
from django import forms

import json
import urllib
from urlparse import urlparse

from django.contrib.auth.models import User


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
