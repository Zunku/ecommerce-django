# Shortcut to
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

# HTTP status code
from rest_framework import status
# REST Framework comes with it's own Request and Response classes, that are simpler and powerful
from rest_framework.decorators import api_view
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

# Serializing objects
from .models import Product, Collection, Customer
from .serializers import ProductSerializer, CollectionSerializer, CustomerSerializer

# API RESTful Views

# Class-based Views
# Converting our Products View Funcions into a Class-based View
class ProductList(APIView):
    def get(self, request):
        queryset = Product.objects.select_related('collection').all()
        serializer = ProductSerializer(
            queryset, many=True, 
            # HyperlinkedRelatedField requires the request in the serializer context, so we need to add context here
            context={'request':request}
            )
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Old Product View Functions
# This decorator replaces the 'request' object with the one that comes with the REST framework
# Inside you have to put a list with the HTTP Methods that are supported
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        # With select_relatad we avoid extra queries when indexing collections on serializer objects
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
        serializer = ProductSerializer(data=request.data, context={'request':request})
        # Validating Data
        # Validation is check if the data fields meets the requirements of the serializer, dtype, lenght, patterns, etc
        # raise_exception will raise an exception if the request is not valid and send a response with http status 400 and include validation errors.
        serializer.is_valid(raise_exception=True)
        # Saving Data/Creating Object .save() saves the dictionary in our database
        serializer.save()
        # validated_data returns a ordered dictionary with the right dtype for each field
        # A RESTFul convention is to return the object and HTTP 201 when creating an object
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductDetail(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product,id=id)
        serializer = ProductSerializer(product, context={'request':request})
        return Response(serializer.data)
    
    def put(self, request, id):
        product = get_object_or_404(Product,id=id)
        serializer = ProductSerializer(product, data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        product = get_object_or_404(Product,id=id)
        if product.orderitem.count() > 0:
            return Response({'error': 'Product cannot be deleted because is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Old Product Detail Views Functions
# Serializing Product objects
@api_view(['GET','PUT', 'DELETE'])
def product_detail(request, id):
    # We are using try despite we are using the get_object_or_404 only for pedagogical purposes
    product = get_object_or_404(Product,pk=id)
    if request.method == 'GET':
        # For convention, if an object does not exist, you have to send HTTP status 404 as response
        # try/excep is not the best method for this
        try:
            # Getting the product object
            # In this moment, the serializer convert the product object to an dictionary
            serializer = ProductSerializer(product, context={'request':request})
            # Under the hood, Django creates a JSON renderer and passes the dictionary to convert it to a JSON object
            # .data Access the python dictionary
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    # Updating an object
    elif request.method == 'PUT':
        # If we put an instance of the class inside the serializer, it will call the update method and will update the atributes with the data in the request, so we need to put the Product.object.get outside of the if
        serializer = ProductSerializer(product, data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    # Deleting an object
    elif request.method == 'DELETE':
        # It's not allowed to delete a product with orderitems, so we need to create a proper response
        if product.orderitem.count() > 0:
            # We can add a dictionary to add a body in the response, it will be converted to JSON
            return Response({'error': 'Product cannot be deleted because is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@api_view()
def customer_list(request):
    queryset = Customer.objects.all()
    serializer = CustomerSerializer(queryset, many=True)
    return Response(serializer.data)

# Excersise: Create a collecction endpoint that shows all the collection instances
# Number of products in each collection
# Allow to create a collection
# A collection_detail endpoint that shows the collection details and allows to delete it and update it

@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.annotate(product_count=Count('product'))
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    collection.product_count = Product.objects.filter(collection_id=pk).count()
    if request.method == 'GET':
        # Using get_object_or_404 for a short and more redable code. Much better than try/except
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.product.count() > 0:
            return Response({'error': 'Collection cannot be deleted because is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Mixins