# Importing serializer for UserCreation
from djoser.serializers import UserCreateSerializer as BaseUCS, UserSerializer as BaseUS
from rest_framework import serializers

# Creating a custom serializer for registering users
class UserCreateSerializer(BaseUCS):
    # We can access birth_date because we have a relationship with user in the Customer model
    birth_date = serializers.DateField()
    
    # Always is better to inherit all from a class and overwrite only the fields you need
    class Meta(BaseUCS.Meta):
        # Adding extra fields to the serializer
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'birth_date']
        
# Custom serializer to show first and last name of current user
class UserSerializer(BaseUS):
    class Meta(BaseUS.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']