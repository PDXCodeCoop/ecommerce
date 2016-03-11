from django.test import TestCase
from models import *
# Create your tests here.
class ProductTestCase(TestCase):
    def setUp(self):
        Product.objects.create(title="Server Box", price=60.00, discount=20.00)

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        product = Product.objects.get(name="Server Box")
        self.assertEqual(product.total(), 40.00)
