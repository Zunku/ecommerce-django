from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product

from .models import User
# We need to add the app to settings.py

# Registering admin model to managing our users
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

# Using Generic Relationships
# Class for managing Tags
# Like a tabular inline class but for generic objects
class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


# Extending Pluggable Apps
# It's importat that each class mantain independency, so any class should know anything about another one
# That's why we need to create a new app called "store_custom" who is gonna know about the two apps

# Creating a custom admin
class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]
    
# Unregister a model from model interfaz
admin.site.unregister(Product)

# Register a model with a custom admin
admin.site.register(Product, CustomProductAdmin)