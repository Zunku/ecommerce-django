from decimal import Decimal
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Sum
from django.db import transaction
from rest_framework import serializers
from .models import Product, Collection, Customer, Review, Cart, CartItem, Order, OrderItem, ProductImage
from .signals import order_created

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
    # Adding an Annotated() field to the model
    product_count = serializers.IntegerField(read_only=True)
    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product_id']
    
    # Getting context from the view and adding product_id to the object creation
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection_id','collection_title' ,'collection_link', 'images']
    
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_tax')
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source='collection'
    )
    collection_title = serializers.StringRelatedField(source='collection', read_only=True)
    # Generating hyperlinks of a related object
    collection_link = serializers.HyperlinkedRelatedField(
        source='collection',
        queryset= Collection.objects.all(),
        # name of the view in urls.py
        view_name='collection-detail',
        required=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Method for MethodField
    def get_price_tax(self, product:Product):
        return product.unit_price * Decimal(1.1)
    
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'title', 'description', 'name']
    
    # Overwriting create() method to change how the review instance is created to add product_id when creating the review
    def create(self, validated_data):
        validated_data['product_id'] = self.context['product_id']
        # With super() we can use the parent method, so we are extending the class with our logic, not totally replacing it
        return super().create(validated_data)
    
# Special serializer of product for cart
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']
        
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_item_price']
        
    total_item_price = serializers.SerializerMethodField(method_name='get_total_item_price')
    product = SimpleProductSerializer()
    
    def get_total_item_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

# Serializer for creating a cartitem, without innecesary fields
class AddCartItemSerializer(serializers.ModelSerializer):
    # Orden matters, if you put product_id after Meta class, it will not work
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    # Overwriting save() method to avoid creating items for repetead products, and instead, update the quantity
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            # Updating existing item
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Creating a new item
            # ** Unpack a dictionary
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance
    

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found')
        return value
    
# Serializer to limit fields when updating a cart item
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    
    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    # Here the serializer looks for a relation, not the ID. The atribute is created based on CartItem.objects.filter(cart=cart)
    items = CartItemSerializer(many=True, read_only=True)
    
    def get_total_price(self, cart:Cart):
        totals_items_prices = [item.quantity * item.product.unit_price for item in cart.items.all()]
        return sum(totals_items_prices)
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']
    product = SimpleProductSerializer(read_only=True)
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'placed_at', 'payment_status', 'orderitems']
        
    orderitems = OrderItemSerializer(many=True, read_only=True)
    
# Serializer for creating an order from a cart
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found')
        elif CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty. Add items to make an order.')
        return cart_id 
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            
            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            # List comprehension to unpack items in cart_items and convert them into order_items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            # bulk_create allow us to save a list of objects at once
            OrderItem.objects.bulk_create(order_items)
            # Deleting the cart for the order, not needed anymore
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)
            
            return order

# Serializer for updating an order and only being able of modify payment_status
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']