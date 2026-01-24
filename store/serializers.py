from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Sum

# Serializers are classes that convert model instances to dictionaries/JSON and vice versa
# Deserialization: convert JSON/dictionaries to model instances
from rest_framework import serializers
from decimal import Decimal
from .models import Product, Collection, Customer, Review, Cart, CartItem

# It's not te best way to serialize, Model Serializers are better
class WrongCollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
    # Adding an Annotated() field to the model
    product_count = serializers.IntegerField(read_only=True)
    
# Creating a class to serialize Products
# It's exactly like defining a model
# Serializers not necesary have to look like model objects, they can have their own fields
# Here I'm using MoelSerializer and still defining each field, but it's just for pedagogical purposes
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'price', 'price_with_tax', 'collection_id','collection_title', 'collection_object' ,'collection_link']
    # Only return external representation information
    id = serializers.IntegerField(read_only=True)
    # We still have to add atributes like max_lenght because later we will use serializers when receiving data to our API
    title = serializers.CharField(max_length=255)
    # source Django asumes that serializer fields/atributes will match models fields/atributes, if not, you need to use this parameter to indicate the model field/atributes source, but is not a good practice changing field names bc you are breaking consistency
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    
    # Custom Serializer Method Field
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_tax')
    
    # Serializing Relationships
    # Accesing the PK of a related object, the most common way. This way we can select the product from a list in the Browsable API
    collection_id = serializers.PrimaryKeyRelatedField(
        # Need a queryset for looking for the related object (collection)
        queryset=Collection.objects.all(),
        source='collection'
    )
    # Accesing to the string representation of a related object
    collection_title = serializers.StringRelatedField(source='collection', read_only=True)
    # Nesting the collection object
    collection_object = CollectionSerializer(source='collection', read_only=True)
    # Generating hyperlinks of a related object
    collection_link = serializers.HyperlinkedRelatedField(
        source='collection',
        queryset= Collection.objects.all(),
        # name of the view in urls.py
        view_name='collection-detail',
        required=False
    )
    
    # Method that will be passed to SerializerMethodField, to create a Custom Serializer Field
    # If we annotate parameters with it's corresponsant type, we will get intelisense
    def get_price_tax(self, product:Product):
        return product.unit_price * Decimal(1.1)

    # Overwriting create() method. This method takes the validated_data and creates a new field "other". It's called by the save() method if we try to create a new product
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other = 1
    #     product.save()
    #     return product
    
    # Overwriting the update() method. It's called by the save() method when trying to update
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance
    
# Model Serializers
# It's a much better way
# This way, there is no need to define the validaton rules two times, in the serializer and the model
# You can always redefine a field if you want to change what is showed in the api
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        # fields that we want to inherit form the model, and new fields
        # Djando first look for this fields in the model, if it don't find any, he will then look for it in the serializer
        fields = ['id', 'first_name', 'last_name', 'full_name']
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    
    def get_full_name(self, customer:Customer):
        return f"{customer.first_name} {customer.last_name}"
    
    # Validation between fields
    # We are overwriting the validate method, in this case makes no senses, just an example
    def validate(self, data):
        if data['password'] != data['confirm_passowrd']:
            return serializers.ValidationError('Passwords do not match')
        return data

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'title', 'description', 'name']
    
    # Customizing how a field is created
    # Overwriting create() method to change how the review field is created to add product_id when creating the review
    def create(self, validated_data):
        validated_data['product_id'] = self.context['product_id']
        # With super() we can use the parent method, so practicaly we are extending the class with our logic, not totally replacing it
        return super().create(validated_data)
    
# Creating another serializer for product to show only some fields when getting a cart object
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
        # cart_item.product 
        return cart_item.quantity * cart_item.product.unit_price

# Serializer for creating a cartitem, without innecesary fields
class AddCartItemSerializer(serializers.ModelSerializer):
    # Orden matters, if you put product_id after Meta class, it will not work
    product_id = serializers.PrimaryKeyRelatedField(
        # Need a queryset for looking for the related object
        queryset=Product.objects.all(),
        source='product'
    )
    # product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    # Overwriting avoid creating items for repetead products, and instead, update the quantity
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product']
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
    
    # Custom validator, it's a naming convention/contract to start validation methods with validate_
    # For each field, Django looks for a method with validate_<field_name> and calls it automaticaly
    # if hasattr(self, f'validate_{field_name}') hasattr looks if the object has a specified method
    # value = getattr(self, method_name)(value) # getattr get the method by it's name, pass the value, execute it and replace value
    # This is called Naming Convention or Naming Contract
    # Value is the POST product_id
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value.id).exists():
            raise serializers.ValidationError('No product with the given ID was found')
        return value.id
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
    
    # Defining static model atributes 
    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    # Here the serializer looks for a relation, not the ID. The atribute is created based on CartItem.objects.filter(cart=cart)
    items = CartItemSerializer(many=True, read_only=True)

    # Is a convention to start the method with get_ when declaring for SerializerMethodField
    def get_total_price(self, cart:Cart):
        # A select related('product') is not needed because the object itself is already related with products
        total_price = cart.items. \
        annotate(total_price_item=ExpressionWrapper(F('quantity')*F('product__unit_price'), output_field=DecimalField())). \
        aggregate(Sum('total_price_item'))
        return total_price['total_price_item__sum']
    
    # A much more easy way using a list comprehension
    def get_total_price_easy(self, cart:Cart):
        totals_items_prices = [item.quantity * item.product.unit_price for item in cart.items.all()]
        return sum(totals_items_prices)