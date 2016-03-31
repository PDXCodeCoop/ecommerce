from serializers import *
from models import *
from rest_framework import viewsets

class OptionCategoryViewSet(viewsets.ModelViewSet):
    queryset = OptionCategory.objects.all()
    serializer_class = OptionCategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
