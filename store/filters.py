# Custom Filter

from django_filters.rest_framework import FilterSet
from .models import Product

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            # There are several keywords to add filters in the documentation, the order matters
            # Creates several query parameters and implement methods automatically
            'collection_id':['exact'],
            'unit_price': ['gt','lt']
        }