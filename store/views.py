# Shortcut to
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count, Sum
from django.db.models import F, ExpressionWrapper, DecimalField
# Djangofilters library
from django_filters.rest_framework import DjangoFilterBackend

# HTTP status code
from rest_framework import status
# REST Framework comes with it's own Request and Response classes, that are simpler and powerful
from rest_framework.decorators import api_view
# Searching, Ordering
from rest_framework.filters import SearchFilter, OrderingFilter
# Pagination default
from rest_framework.pagination import PageNumberPagination
# Mixins are classes that encapsulate some patterns of code (Create, List, Retrive, Delete, Update)
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin
# Generic Views are common views that inherit from mixins
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

# Our app
from .models import Product, Collection, OrderItem, Review, Cart, CartItem
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartItemSerializer, CartSerializer
from .filters import ProductFilter
from .pagination import DefaultPagination

# API RESTful Views
# View Sets
# ModelViewSet is just a combination of all the Mixins
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    # Generic Filters/Backend, beside giving us generic filters, also implement a button to change between filters
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # We only have to choose the fields we want to filter (Old)
    filterset_fields = ['collection_id']
    # Custom Filters - Djangofilters include a lot of prebuild filtering backends
    filterset_class = ProductFilter
    # Pagination - Default page size is specified on settings.py/REST_FRAMEWORK
    pagination_class = DefaultPagination
    # Searching - Django restframework give us a backend for seach for words
    # Also we can search for later classes like collection__title
    search_fields = ['title', 'description']
    # Ordering - Django restframework give us a backend for ordering by fields
    ordering_fields = ['unit_price', 'title', 'last_update']
    # Filters (Old)
    # Overwriting get_query to be able to filter products by collection
    # def get_queryset(self):
    #     queryset = Product.objects.select_related('collection').all()
    #     # query_parms ?
    #     # .get() returns None in case that the key don't exists
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset
        
    def get_serializer_context(self):
        return {'request':self.request}
    
    # We have the delete method to this, because ModelViewSet need it 
    # *args & **kwargs are used for a function to be able to recive aruguments without needed to know how many neither how much. Allow to overwrite methods without breakup
    # *args posicional arguments
    # **kwargs named arguments (dictionary)
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)

# Creating Generic API Views (Old)
# Only with this we can replace the get and post methods, and also creates a form to enter data in HTML in the Browsable API
# class ProductList(ListCreateAPIView):
    
    # Generic Views have queryset and serializer class atributes, that are better for simple useges
    # queryset = Product.objects.select_related('collection').all()
    # serializer_class = ProductSerializer
    
    # Generic Views Methods are better for complex usages, that need some logic
    # def get_queryset(self):
    #     return Product.objects.select_related('collection').all()
    
    # def get_serializer_class(self):
    #     return ProductSerializer
    
    # def get_serializer_context(self):
    #     return {'request':self.request}

    # # Class-based Views (Old)
    # # Converting our Products View Funcions into a Class-based View
# class ProductList(APIView):
    # def get(self, request):
    #     queryset = Product.objects.select_related('collection').all()
    #     serializer = ProductSerializer(
    #         queryset, many=True, 
    #         # HyperlinkedRelatedField requires the request in the serializer context, so we need to add context here
    #         context={'request':request}
    #         )
    #     return Response(serializer.data)

    # def post(self, request):
    #     serializer = ProductSerializer(data=request.data, context={'request':request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


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

# (Old)
class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Change the parameter needed for calling the view, useful when you *really* need to change it
    # lookup_field = 'id'
    # Old get/set methods
    # def get(self, request, id):
    #     product = get_object_or_404(Product,id=id)
    #     serializer = ProductSerializer(product, context={'request':request})
    #     return Response(serializer.data)
    
    # def put(self, request, id):
    #     product = get_object_or_404(Product,id=id)
    #     serializer = ProductSerializer(product, data=request.data, context={'request':request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)
    
    # Customizing/Overwrite the delete Generic View Function
    def delete(self, request, pk):
        product = get_object_or_404(Product,pk=pk)
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

# If we only want a view set to read_only, we can use the ReadOnlyModelViewSet
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_serializer_context(self, *args, **kwargs):
        # In this case kwargs contain URL parameters
        # In the URL is defined with the  lookup parameter, and a _pk is added automaticaly
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
# Here we don't want the PUT neither the LIST method, so we are going to use a GenericViewSet, and use separated Mixins
class CartViewSet(CreateModelMixin, GenericViewSet, DestroyModelMixin, RetrieveModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()