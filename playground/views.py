# function to use templates
from django.shortcuts import render
# Send a http response
from django.http import HttpResponse
from store.models import Product

# Create your views here.
# View function: request -> response
# request handler
# In some frameworks is called actions
# view no es muy adecuado porque hace referencia a algo que el usuario puede ver, en django a eso se le llama templates

# Creating our first view function
# It have to be mapped to a URL
def say_hello(request):
    # Pull data from db
    # Transform
    # Send email
    # A basic way to return a httpresponse
    return HttpResponse('Hello World')

# http response with django templates, a way to front-end your requests (not common)
def render_say_hello(request):
    # Product.objects Returns a manager object
    # Creating a query_set. An object that encapsulate a query
    query_set = Product.objects.all()
    # Evaluating query_set, indexing all elementos from Product table
    for product in query_set:
        print(product)
    # http_request, template_name, variable
    return render(request, 'hello.html', {'name': 'Mosh'})