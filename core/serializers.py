# Importing serializer for UserCreation
from djoser.serializers import UserCreateSerializer as BaseUCS
from rest_framework import serializers

# Creating a custom serializer for registering users
class UserCreateSerializer(BaseUCS):
    birth_date = serializers.DateField()
    
    # Always is better to inherit all from a class and overwrite only the fields you need
    class Meta(BaseUCS.Meta):
        # Adding extra fields to the serializer
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
        
    