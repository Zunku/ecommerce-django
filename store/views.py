from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
# REST Framework comes with it's own Request and Response classes, that are simpler and powerful
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .filters import ProductFilter
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order, ProductImage
from .pagination import DefaultPagination
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartItemSerializer, CartSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermission

# API RESTful Views
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').prefetch_related('images').all()
    serializer_class = ProductSerializer
    # Generic Filters/Backend, beside giving us generic filters, also implement a button to change between filters
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Custom Filters
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'title', 'last_update']
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)

class ProductImageView(ModelViewSet):
    serializer_class = ProductImageSerializer
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because is associated with a product.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_serializer_context(self, *args, **kwargs):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
# Using individual mixins bc it's not needed UPDATE neither LIST
class CartViewSet(CreateModelMixin, 
                  GenericViewSet, 
                  DestroyModelMixin, 
                  RetrieveModelMixin):
    # Eager loading items and product to avoid generating extra queries
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    # Special atribute to determine the allowed http methods, have to be in lowercase 
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    
    # Here we determine which serializer are we going to use depending on the HTTP method
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
# View set for the User Profile
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [FullDjangoModelPermissions]

    # Action with a custom model permission
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')
    
    # Action to get or create the customer profile
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # Every request have an user atribute that will contain data about the user or anonymus if not logged 
        customer = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
class OrderViewSet(ModelViewSet):
    
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    # Indexing a diferent query depending on the permissions
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.prefetch_related('orderitems').all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    # Overwriting create function to save order and retrieve the order with separated serializers, and therefore show diferent fields
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
        
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
        
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.prefetch_related('product')
    serializer_class = OrderItemSerializer