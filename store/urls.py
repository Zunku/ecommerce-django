
# Object to define URLS
from django.urls import path
# Our views module
from . import views

# Special variable that stores urls patterns objects, receive requests, and send them to it's correspondant views
# URL conf module, each app can have it's own
urlpatterns = [
    # path('URL/', view function)
    # All our routes must end with /
    # as_view() Convert the class to a regular function-based view
    path('products/', views.ProductList.as_view()),
    # This way we add a parameter <dtype:parameter>, make sure to select the right name for lookup_field
    path('products/<int:id>', views.ProductDetail.as_view()),
    path('collections/', views.collection_list),
    # name Is nedded if you want to use this view in methods that need to access the view like HyperlinkedRelatedField
    path('collections/<int:pk>', views.collection_detail, name='collection-detail'),
    path('customers/', views.customer_list)
]