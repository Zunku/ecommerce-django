
# Object to define URLS
from django.urls import path
# Our views module
from . import views

# Special variable that stores urls patterns objects, receive requests, and send them to it's correspondant views
# URL conf module, each app can have it's own
urlpatterns = [
    # path('URL/', view function)
    # All our routes must end with /
    path('products/', views.product_list),
    # This way we add a parameter <dtype:parameter>, make sure to select the right name for lookup_field
    path('products/<int:id>', views.product_detail),
    path('products-short/<int:id>', views.product_detail_shortcut),
    # name Is nedded if you want to use this view in methods that need to access the view like HyperlinkedRelatedField
    path('collections/<int:pk>', views.collection_detail, name='collection-detail'),
    path('customers/', views.customer_list)
]