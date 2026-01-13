import datetime

# function to use templates
from django.shortcuts import render
# Send a http response
from django.http import HttpResponse
# Django exceptions managment
from django.core.exceptions import ObjectDoesNotExist
# Q is short for Query. Q objects
# F is a short for Field. Allows us to reference a particular field.
from django.db.models import Q, F

from store.models import Product, Order, OrderItem

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

def manager_objects(requests):
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
        # pk: Primary Key
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
    # Indexing
    query_set7 = Product.objects.filter(inventory=F('unit_price'))
    return render(request, 'hello.html', {'name': 'Mosh', 'products': list(query_set6)})