import datetime

# function to use templates
from django.shortcuts import render
# Send a http response
from django.http import HttpResponse
# Django exceptions managment
from django.core.exceptions import ObjectDoesNotExist
# Q is short for Query. Q objects
# F is a short for Field. Allows us to reference a particular field.
# Values allow us to use Values inside querysets 
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
# Aggregate functions, the same as in SQL
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
# SQL CONCAT Function
from django.db.models.functions import Concat

# Model that represent the ContentType table
from django.contrib.contenttypes.models import ContentType

from store.models import Product, Order, OrderItem, Customer, Collection

from tags.models import TaggedItem

# Create your views here.
# View function: request -> response
# request handler
# In some frameworks is called actions
# view no es muy adecuado porque hace referencia a algo que el usuario puede ver, en django a eso se le llama templates

# Creating our first view function
# It have to be mapped to a URL, so the functions is called when a request is sended to that URL
def say_hello(request):
    # Pull data from db
    # Transform
    # Send email
    # A basic way to return a httpresponse
    return HttpResponse('Hello World')

# http response with django templates, a way to front-end your requests (not common)
def render_say_hello(request):
    
    # http_request, template_name, variable
    return render(request, 'hello.html', {'name': 'Mosh'})

def manager_objects(request):
    # Product.objects Returns a manager object
    # Creating a query_set. An object that encapsulate a query
    query_set = Product.objects.all()
    
    # Evaluating query_set, indexing all elementos from Product table
    for product in query_set:
        print(product)
        
    # You can add more complex querys to the query_set before evaluating
    query_set.filter().order_by()
    
    # Managing exceptions
    try:
        # Indexing an element from our table, returns an object
        # pk: Primary Key. Useful bc we don't have to remember the name of the field
        product = Product.objects.get(pk=1)
    except ObjectDoesNotExist:
        pass
    
    # filter returns a query_set
    # first returns the first element of a query_set, if empty returns None
    # This way we avoid excepcion managment
    product = Product.objects.filter(pk=0).first()
    
    # Returns the count of Product table, not a query_set
    product_count = Product.objects.count()
    
    # exist returns a boolean evaluating if the element exist
    exists = Product.objects.filter(pk=0).exists()
    
    
def filtering(request):
    
    # Indexing orders where customer_id == 5
    query_set = Order.objects.filter(customer_id=5)
    
    # You can't use boolean expresions like price > 20, bc that returns a boolean and means nothing
    # Insted you use a lookup: column__gt=20 where gt is a lookup that means "Greater Than"
    query_set1 = Product.objects.filter(unit_price__gt=20)
    
    # You can also use this syntaxis to filter by an specific value of the attribute/column
    # Indexing products with colection_id == (102 | 103 | 104)
    query_set2 = Product.objects.filter(collection__id__range=(102, 103, 104))
    
    # Indexing products where title contains 'coffee'.
    # i = not case sensitive
    query_set3 = Product.objects.filter(title__icontains='coffee')
    
    # Indexing products where last update was in January, 2021
    # You can add multiple conditions just with a comma
    query_set4 = Product.objects.filter(last_update__year=2021, last_update__month=1)
    
    # Indexing products where description is null
    query_set5 = Product.objects.filter(description__isnull=True)
    
    # A Q object encapsulate a keyword argument/query expression
    # Indexing products where inventory are lower than 10 | unit price (~)not lower than 20
    # ~ It's the not operator
    query_set6 = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))
    
    # F objects allows us to reference a particular field
    # Also using __ we can reference related tables
    # Indexing products where inventory == collection table featured product id
    query_set7 = Product.objects.filter(inventory=F('collection__featured_product_id'))
    
    return render(request, 'hello.html', {'name': 'Mosh', 'products': list(query_set7)})

def sort_limit(request):
    # Sorting products by title. - for inverse order
    # We can also order by several fields
    # reverse() reverse the direction of the sort
    query_set = Product.objects.order_by('unit_price','-title').reverse()
    
    # Limiting objects
    # Indexing the first object ordering by unit_price
    first_product = Product.objects.order_by('unit_price')[0]
    first_product = Product.objects.earliest('unit_price')
    
    # Indexing the first object ordering by -unit_price
    last_product = Product.objects.latest('unit_price')
    
    # We can limit objects with the same python slicing [:] syntax
    # Indexing the first 5 objects
    query_set1 = Product.objects.all()[:5]
    # Indexing object 5 - 10
    query_set1 = Product.objects.all()[5:10]
    
    # Select fields
    # .values() Allow us to index only selected files from a table, with __ allows us to index related tables, making joins
    # Each object is a dictionary, not a product instance like before
    query_set2 = Product.objects.values('id', 'title', 'collection__title')
    
    # .values_list() Returns tuples instead of dictionaries
    # flat=True Deletes the tuple and returns the string alone when only one field
    query_set2 = Product.objects.values_list('id', 'title', 'collection__title', flat=True)
    
    # Distinc
    # .distinct() Index only unique values
    ordered_products = Product.objects.values('title', 'id').filter(id=F('orderitem__product_id')).distinct().order_by('title')
    
    # .defer() Exlude a field, be careful bc if you index later the same field, you will end with a lot of querys
    # Returns objects
    query_set4 = Product.objects.defer('description')
    
    # Related tables
    # select_related(1) Index a related table and makes a inner join, for relations -:1 with parent
    # To access that filed in templates you need to product.collection.title for example
    query_set5 = Product.objects.select_related('collection').all()
    
    # prefetch_related(n) Index a related table, for relations -:n with parent
    # Makes two querys, one for indexing the first table, and the other one the related table
    query_set6 = Product.objects.prefetch_related('promotions').all()
    
    # Get the last 5 orders with their customer and items (including products)
    # For reverse relationships, Django uses the parentmodelname_set name
    # We can expand our query to add products with __
    query_set7 = Order.objects.order_by('-placed_at')[:5].select_related('customer').prefetch_related('orderitem_set__product')
    
    return render(request, 'hello.html', {'name': 'Mosh', 'orders': query_set7})

def aggregate_func(request):
    
    # Aggregate functions
    # Count all the fields of that column that are not null, returns a dictionary
    # We can pass a keyword argument to rename the dictionary key
    result = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))
    
    # Annotating objects
    # .annotate() Add a new field to the table, fieldname = defaultvalue
    # Value() Is an expression that allow us to use Values
    # It not saves the query in the database
    queryset1 = Customer.objects.annotate(is_new=Value(True))
    
    # You can also use field references with F Objects and make computations
    # Creating a new id to each row with +1
    queryset2 = Customer.objects.annotate(new_id=F('id')+1)
    
    # Database functions
    # Func() expression class allow us to use SQL Functions like CONCAT
    # You need to use Values(' ') bc if not django thinks it's a columnname
    # CONCAT
    queryset3 = Customer.objects.annotate(
        full_name=Func(F('first_name'), Value(' '), 
                       F('last_name'), function='CONCAT')
    )
    
    # A short way using the Concat() class
    queryset4 = Customer.objects.annotate(
        full_name=Concat('first_name', Value(' '), 'last_name')
    )
    
    # Grouping data
    # Grouping orders by customers using Count()
    queryset5 = Customer.objects.annotate(
        # When you use an aggregate funcion inside an annotate() it automaticaly group 
        # With Count() if we want to use a reverse relation ship, you don't have to use fieldname_set, just fieldname
        orders_count=Count('order')
    )
    
    # Expression Wrappers
    # Allow us to wrap complex expressions (such as arithmetic on F() with different types) and select the output field (need to be imported)
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    queryset6 = Product.objects.annotate(
        discounted_price=discounted_price
    )
    
    # Custom manager, returns the tags for the specified object and ID
    # For some reason intelisense don't work, but it still works
    queryset7 = TaggedItem.objects.get_tags_for(Product, 1)

    # Creating Objects/Insert
    collection = Collection()
    collection.title = 'Sports'
    collection.featured_product = Product(pk=2)
    # Every model have a method save insert a new record in our database
    collection.save()
    
    return render(request, 'aggregate_func.html', {'name': 'Daniel', 'result': queryset7})

def updating_objects(request):

    # Updating Objects
    # We have to access directly to the object because otherway, if we try to update only one field of the object, we will generate data loss
    collection = Collection.objects.get(pk=18)
    collection.title = 'E Sports'
    collection.featured_product = None
    # Every model have a method save that saves the record in our database
    collection.save()
    
    # Method 2, it's a bit faster, but makes our code a bit fragile because we can't update the parameter automatically with F2
    Collection.objects.filter(pk=18).update(featured_product=None)
    
    # Deleting Objects
    # This way we delete a single object
    collection = Collection(pk=11)
    collection.delete()
    
    # This way we delete several objects (with id greather than 5)
    # We have to first create a queryset we want to delete
    Collection.objects.filter(id__gt=5).delete()
    return render(request, 'aggregate_func.html', {'name': 'Daniel', 'result': collection})

def transactions(request):
    
    # Transactions
    # A way to make several changes on our database in an anomic way, meaning all changes should be saved togheter. If one changes fails then all changes should be rolled back
    # In relatinoal datababases, we should alawys creater the father before the child
    # order = Order()
    # order.customer_id = 1
    # order.save()
    
    # item = OrderItem()
    # item.order = order
    # item.product_id = 1
    # item.quantity = 1
    # item.unit_price = 10
    # item.save()
    
    queryset = Customer.objects.annotate(
        sales_per_customer=Count('order__orderitem')
    ).values_list('first_name','order__orderitem')
    return render(request, 'aggregate_func.html', {'name': 'Daniel', 'result': queryset})