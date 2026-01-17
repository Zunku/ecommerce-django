# It's useful to sort your imports by alphabeth

from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
# Importing models module from the same directory
from . import models

# Here you can customize the admin interfaz of this app
    
# Registering Collection model, now it will be displayed in the admin interfaz
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']
    
    # Adding a Computed Column
    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # Providing Links to Other Pages
        # reverse() Returns an url inside the Django project. It gives you extra security because avoid bugs in case of changing links. Syntax: admin:app_model_page
        # changelist is the name of the page where you can edit your registries
        # We filter only the products from the selected colection with ?
        # ? Is a query parameter, allows you to modify of an URL is showed, for filters, searches, options
        # Wrapping an expression with () allows you to break it in multiple lines
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
    # Filter table title
    title = 'Inventory'
    # Query parameter name (you can choose anything)
    parameter_name = 'inventory'
    
    # Here you define the items that will apear in the custom filter
    def lookups(self, request, model_admin):
        return [
          # ('Value for filtering', 'Value that will be showed in the table')
            ('<10', 'Low')
        ]
        
    # Here we implement the filtering logic
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

# In this class we can specify how we want to view/edit our products
# For convention you need to use ModelnameAdmin
class ProductAdmin(admin.ModelAdmin):
    # Customizing Forms (a form to add new objects to the db)
    # Autocomplete the field with a search method from the model
    autocomplete_fields = ['collection']
    # Fill automaticaly one field with another one
    prepopulated_fields = {
        'slug': ['title']
    }
    # Exclude fields from the form
    # readonly_fields to converte a field to read only, fields to select the fields to show
    exclude = ['promotions']
    # List of actions
    actions = ['clear_inventory']
    search_fields = ['title']
    # What fileds will be diaplayed
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    # What field will de editable
    list_editable = ['unit_price']
    # Adding Filtering and our Custom Filter class
    list_filter = ['collection', 'last_update', InventoryFilter]
    # How many products will be displayed per page
    list_per_page = 10
    # Is like .select_related. Allows you to select a related table. This avoid creating extra querys for each product
    list_select_related = ['collection']
    
    # Adding a Computed Column
    # If inventory < 10 returns 'Low'
    # This decorator allow to add atributes to a display function, like ordering
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    
    # Selecting Related Objects. In this case is not needed because collection already returns it's title when it's called it's just an example
    def collection_title(self, product):
        return product.collection.title
    
    # Creating Custom Actions
    @admin.action(description='Clear inventory')
    # Name of the action
    def clear_inventory(self, request, queryset):
        # Actual action
        updated_count = queryset.update(inventory=0)
        # Shows a message to the user when the action is aplied
        self.message_user(
            request, 
            f'{updated_count} products were succcessfully updated.',
            # Type of message
            messages.ERROR
        )
        
# Registering Product model with its ProductAdmin class
admin.site.register(models.Product, ProductAdmin)


# You can also register the model with a decorator
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
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

# Editing Childs Using Inlines
# Is a way to create a new object when you are creating another object
# In this case, we want to be able to create orderitems when we are creating an order
# Also you can use admin.StackedInline insted to separate fields by line
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    # min items to enable the object creation
    min_num = 1
    # max items to enable the object creation
    max_num = 10
    # extra lines that are created automaticaly
    extra = 0
    model = models.OrderItem

# Registering Order model    
@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id','placed_at', 'payment_status', 'customer']
    list_per_page = 10
    
