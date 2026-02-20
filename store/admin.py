from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
# Importing models module from the same directory
from . import models

    
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    # Adding a Computed Column
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist') 
            + '?'
            # Here we can add several keys to use in the query parameter, and urlencode() will encode them automatically
            + urlencode({
                'collection__id': str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    # Overriding the Base QuerySet. Each ModelAdmin class have this method
    def get_queryset(self, request):
        # Here we are modifiying the base queryset adding annotate to calculate the products_count
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )
        
# Creating a custom filter
class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'
    
    # Defining items that will apear
    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]
        
    # Filtering logic
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']
    
    def thumbnail(self, instance:models.ProductImage):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class=thumbnail>')
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }
    exclude = ['promotions']
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    search_fields = ['title']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    
    
    # Custom Action for clearing inventory of a product
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, 
            f'{updated_count} products were succcessfully updated.',
            # Type of message
            messages.ERROR
        )
    
    # Class for showing media
    class Media:
        # Static assets to load
        css = {
            'all': ['store/styles.css']
        }

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['user__first_name', 'user__last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    # Adding Search to the List Page
    # __istartswith Is a lookup to indicate no-sesitive string start
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
            )

# Inline for adding items when creating an order
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    # min items to enable the object creation
    min_num = 1
    # max items to enable the object creation
    max_num = 10
    # extra lines that are created automaticaly
    extra = 0
    model = models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id','placed_at', 'payment_status', 'customer']
    list_per_page = 10