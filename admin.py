from django.contrib import admin
from django import forms
from models import *
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget

class OptionInline(admin.TabularInline):
    model = Option

class ProductInline(admin.TabularInline):
    model = Product

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductOrderInLine(admin.TabularInline):
    model = ProductOrder

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductImageInline, ]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ ProductInline, ]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(OptionCategory)
class OptionCategoryAdmin(admin.ModelAdmin):
    inlines = [ OptionInline, ]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductOrderInLine,
    ]


admin.site.register(Accessory)
admin.site.register(Option)
admin.site.register(Shipping)
admin.site.register(BillingInfo)
admin.site.register(Coupon)
