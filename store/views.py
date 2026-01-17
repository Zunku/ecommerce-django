# Shortcut to
from django.shortcuts import get_object_or_404
# REST Framework comes with it's own Request and Response classes, that are simpler and powerful
from rest_framework.decorators import api_view
from rest_framework.response import Response
# HTTP status code
from rest_framework import status

# Serializing objects
from .models import Product, Collection, Customer
from .serializers import ProductSerializer, CollectionSerializer, CustomerSerializer

# API RESTful Views

# This decorator replaces the 'request' object with the one that comes with the REST framework
# Inside you have to put a list with the HTTP Methods that are supported
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        # With select_relatad we avoid extra queries when indecing collections on serializer objects
        queryset = Product.objects.select_related('collection').all()
        # many=True to indicate that the serializer have to iterate the object
        serializer = ProductSerializer(
            queryset, many=True, 
            # HyperlinkedRelatedField requires the request in the serializer context, so we need to add context here
            context={'request':request}
            )
        return Response(serializer.data)
    elif request.method == 'POST':
        # Deserializating Objects
        # .data Access the JSON data
        serializer = ProductSerializer(data=request.data)
        # Validating Data
        # raise_exception will raise an exception if the request is not valid and send a responde with http status 400 and inclue validation errors
        serializer.is_valid(raise_exception=True)
        # Saving Data .save() saves the dictionary in our database
        serializer.save()
        # validated_data returns a ordered dictionary with the right dtype for each field
        print(serializer.validated_data) # Not needed
        return Response('ok')
    
# Serializing Product objects
@api_view()
def product_detail(request, id):
    # For convention, if an object does not exist, you have to send HTTP status 404 as response
    try:
        # Getting the product object
        product = Product.objects.get(pk=id)
        
        # In this moment, the serializer convert the product object to an dictionary
        serializer = ProductSerializer(product)
        
        # Under the hood, Django creates a JSON renderer and passes the dictionary to convert it to a JSON object
        # .data Access the python dictionary
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Using get_object_or_404 for a short and more redable code
@api_view()
def product_detail_shortcut(request, id):
    product = get_object_or_404(Product, pk=id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view()
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)

@api_view()
def customer_list(request):
    queryset = Customer.objects.all()
    serializer = CustomerSerializer(queryset, many=True)
    return Response(serializer.data)