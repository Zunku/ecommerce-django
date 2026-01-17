from django.db import models
# Module for Data Validation
from django.core.validators import MinValueValidator

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    
# Product class that inherit from models.Model class
# Django generate our database automatically based on our models.
# Django generate the primary_key automatically for each model
# This will generate a table 'Products' with a 'title' column
class Product(models.Model):
    # Assigning an atribute title with Char data field
    title = models.CharField(max_length=255)
    # slug is an extension of the url to help search motors to find an object. Usually a string related to the object
    slug = models.SlugField()
    # A better data field for large text
    # Data Validation
    # blank is an argument to allow empty text in the object form
    description = models.TextField(null=True, blank=True)
    # For monetary values always use DecimalField
    # Better than float bc it don't have rounding issues
    # The max price of our products will be 9999.99
    unit_price = models.DecimalField(max_digits=6, 
                                     decimal_places=2,
                                     # Data Validation
                                     # Here you can put your validators, (minvalue, message=optional)
                                     validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    # To storing the date of the last object update
    # auto_now=True Automatically saves the current date on this field
    last_update = models.DateTimeField(auto_now=True)
    # If the referenced class is after this one, you can pass it as a string
    collection = models.ForeignKey('Collection', on_delete=models.PROTECT)
    
    # Defining a Many to Many relationship between two models
    # related_name allows you to change the name of the related class field. If you do this, you have to be consistent and change all the models related_name. It's better to stick with Django convention
    promotions = models.ManyToManyField(Promotion, blank=True)
    
    # Changing the object representation when you convert it to a string
    def __str__(self):
        # Now it will return it's title
        return self.title
    
    # Creating a Meta class to define the specific order of our collection objects
    # A Djando Meta class it's a way to configure our models. Are instructions for Django
    class Meta:
        # Allows you to define an order
        ordering = ['title']
    
class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    
    # Uppercase to indicate that this is a fix list of values, we don't have to mess with it
    # Defining  a list of choices for membership field
    
    # To avoid having to change to values when changing the default value for membership, we create a single variable for each valu
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
        # Change db table name, is not recomended because you are breking the convention and also have to change every table name to make consistency
        db_table = 'store_customers'
        # indexes is a way to optimize querys
        indexes = [
            models.Index(fields=['last_name', 'first_name'])
        ]
        ordering = ['first_name', 'last_name']
        
    def __str__(self):
        # Now it will return it's first_name
        return f'{self.first_name} {self.last_name}'
    
class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    # We should never delete orders, because orders represent our sales
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
    
# Defining a 1 to 1 relationship
class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    # OneToOneField is a model that allows you to create a One To One relationship with the parent, requieres the parent model. Django creates the reverse relationship automaticaly for any relationship
    # You have to choose which class will be the parent, you need to think like "Each customer have an address". It can't exist an address without customer
    # on_delete allows you to control what will happen with the child when the parent is deleted. model.CASCADE deletes the child when the parent is deleted.
    # primary_key forces this field to be unique, avoiding a 1 to * relationship
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    zip = models.CharField(max_length=255)
    
class Collection(models.Model):
    title = models.CharField(max_length=255)
    # related_name = '+' Tells Django not to create the reverse relationship. Useful to avoid conflicts on a circular relationship
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

    # Changing the object representation when you convert it to a string
    def __str__(self):
        # Now it will return it's title
        return self.title
    
    # Creating a Meta class to define the specific order of our collection objects
    # A Djando Meta class it's a way to configure our models. Are instructions for Django
    class Meta:
        # Allows you to define an order
        ordering = ['title']
        
# Defining a * to 1 relationship with ForeignKey
class OrderItem(models.Model):
    # ForeignKey: It's a reference to another model, like say "this registry belongs to another one". Allows you to create a * to 1 relationship with the parent. Each Item saves an OrderID.
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    # Despite we already have the product price in the product model, we should always store the price of the product at the order time
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
# Creating and association class. A class that represent the atributes that will have the association between two classes
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    