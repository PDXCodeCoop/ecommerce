from django.forms import widgets
from rest_framework import serializers
from django.contrib.auth.models import User
from models import Product, Category, Option, OptionCategory

class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('title', 'price')

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'slug')


class OptionCategorySerializer(serializers.HyperlinkedModelSerializer):
    option_set = serializers.StringRelatedField(many=True)
    class Meta:
        model = OptionCategory
        fields = ('title', 'slug', 'option_set')

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    options = OptionCategorySerializer(many=True, read_only=True)
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ('__all__')
