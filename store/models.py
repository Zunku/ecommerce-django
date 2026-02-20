# Importing settings module to use AUTH_USER_MODEL and mantain independency
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4

from .validators import validate_file_size

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=6, 
                                     decimal_places=2,
                                     validators=[MinValueValidator(1)])
    
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey('Collection', on_delete=models.PROTECT, related_name='product')
    promotions = models.ManyToManyField(Promotion, blank=True)
    
    # Changing the object representation when you convert it to a string
    def __str__(self):
        # Now it will return it's title
        return self.title
    
    class Meta:
        ordering = ['title']
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images', validators=[validate_file_size])

class Customer(models.Model):
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    
    # Uppercase to indicate that this is a fix list of values, we don't have to mess with it 
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    
    # This class it's for change metadata
    class Meta:
        db_table = 'store_customers'
        ordering = ['user__first_name', 'user__last_name']
        # Creating custom model permission
        permissions = [
            ('view_history', 'Can view history')
        ]
        
    # Creating User Profiles. Customer model represent User Profile
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    
class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    # We should never delete orders, because orders represent our sales, that's why we user PROTECT
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    
    PS_PENDING = 'P'
    PS_COMPLETE = 'C'
    PS_FAILED =  'F'
    PAYMENT_STATUS_CHOICES = [
        (PS_PENDING, 'Pending'),
        (PS_COMPLETE, 'Complete'),
        (PS_FAILED, 'Failed')
] 
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PS_PENDING)
    
    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]
    
class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    zip = models.CharField(max_length=255)
    
class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    # Despite we already have the product price in the product model, we should always store the price of the product at the order time, because price can change after making an order
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    # GUID: Globally Unique Identifier. Are an unique ID of 32 characters that help to avoid hackers access to our URLs, using simple IDs it's ultra easy for a third party to access these endpoints
    # Cart's will be anonymus and public, a new client can make a cart without an account, that's why GUID are necesary, but as people place orders, we are gonna move this records to Order and OrderItem tables, in those tables we are not gonna use GUIDs, because the Orders API is gonna be secure and not open to anonymous users, a client has to autenticate and be autorized to acces a particular order
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateField(auto_now_add=True)
    
class CartItem(models.Model):
    class Meta:
        # Unique constraint
        # We want to make sure we only have a single instance of a product in our shoping cart. If the client add the same product to the same cart multiple times, we don't want to create another CartItem instance, instead, we want to increase the quantity
        # Here we can have multiples unique constraints on diferent fields, on each list we can add a constraint
        unique_together = [['cart', 'product']]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    
        
class Review(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    
class Pepitoria(models.Model):
    title = models.CharField(max_length=255)