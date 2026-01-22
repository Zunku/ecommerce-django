# A function to make pretty printss
from pprint import pprint
# Object to define URLS
from django.urls import path
# Our views module
from . import views
# Routers are objects that help us to generate URL Patterns to access our views
from rest_framework.routers import DefaultRouter
# Nested routers, routers to nest several URLs ex: products/1/reviews/1
from rest_framework_nested import routers

router = DefaultRouter()
# # DefaultRouter also creates an API Root Page that shows the endpoints for this app
# # register('prefix',ViewSet) Here we can choose the endpoint prefix for our view
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)

# Nesting routes
# (parent_router, 'parent prefix', parameter_name)
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
# Registering child resources ('prefix', ViewSet, prefix_for_urlpatterns) basename: used to generate URL patterns ex: product-review-list, product-review-detail
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
cart_items_router.register('cart-items', views.CartItemSet, basename='cart-items')
urlpatterns = router.urls + products_router.urls + cart_items_router.urls

# Adding extra routes to our urlpatterns
# urlpatterns = [
#     path(r'', include(router.urls))
# ]

# Special variable that stores urls patterns objects, receive requests, and send them to it's correspondant views
# URL conf module, each app can have it's own
# Old
# urlpatterns = [
    # path('URL/', view function)
    # All our routes must end with /
    # as_view() Convert the class to a regular function-based view
    # path('products/', views.ProductList.as_view()),
    # # This way we add a parameter <dtype:parameter>, make sure to select the right name for lookup_field
    # path('products/<int:pk>', views.ProductDetail.as_view()),
    # path('collections/', views.CollectionList.as_view()),
    # # name Is nedded if you want to use this view in methods that need to access the view like HyperlinkedRelatedField
    # path('collections/<int:pk>', views.CollectionDetail.as_view(), name='collection-detail')
# ]