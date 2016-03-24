from django.forms import widgets
from rest_framework import serializers
from django.contrib.auth.models import User
from models import Product, Accessory, Option

class AccessorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Accessory
        fields = ('title', 'price')

class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('title', 'price', )

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    accessories = AccessorySerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('title', 'accessories')
