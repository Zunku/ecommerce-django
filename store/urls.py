from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

# Base routes
router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

# Nested routes
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
order_items_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')

# Registering child resources
products_router.register('images', views.ProductImageView, basename='product-images')
cart_items_router.register('cartitems', views.CartItemViewSet, basename='cart-items')
order_items_router.register('orderitems', views.OrderItemViewSet, basename='order-items')
urlpatterns = router.urls + products_router.urls + cart_items_router.urls