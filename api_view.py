from serializers import *
from models import *
from rest_framework import viewsets

#Profile/User
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
