from django.db import models
from django import forms
from easy_thumbnails.fields import ThumbnailerImageField
from ckeditor.fields import RichTextField

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

# Create your models here.
class Product(models.Model):
    mainimage = ThumbnailerImageField(upload_to='products', blank=True)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
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

"""
Forms Models
"""

class AccessoriesForm(forms.Form):
    class Meta:
        model = Product
        fields = ['accessories']
    accessories = forms.ModelMultipleChoiceField(
        queryset = Product.objects.filter(),
        widget  = forms.CheckboxSelectMultiple,
    )

class OptionsForm(forms.Form):
    class Meta:
        model = Product
        fields = ['options']
    options = forms.ModelMultipleChoiceField(
        queryset = OptionCategory.objects.all(),
        widget  = forms.CheckboxSelectMultiple,
    )
