from django.contrib import admin
from django import forms
from models import *
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget



class ProductOrderInLine(admin.TabularInline):
    model = ProductOrder

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductOrderInLine,
    ]

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductAdmin(admin.ModelAdmin):
    inlines = [ ProductImageInline, ]

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Feature)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shipping)
admin.site.register(BillingInfo)
admin.site.register(Coupon)
