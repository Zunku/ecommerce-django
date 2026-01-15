from django.db import models

# With ContentType we can create generic relatioships between our models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Tag(models.Model):
    label = models.CharField(max_length=255)
    
class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    # To being able to reuse this app, we need to mantein independency, so we don't have to simply from store.models import Product
    # Insted we need two things to identify any object in our aplication:
    # Type/table (product, video, article):
    # ContentType Represent the type of the object in our aplication, is a way to decoupling
    # The ContentTypeID of each model is stored on django_content_type table, we need it to use this app
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # ID/record
    # We are asumming that each table will have a primary key
    # Here is the id of the object we want to tag
    object_id = models.PositiveIntegerField()
    # To read the actual object that a particular tag is applied to
    content_object = GenericForeignKey()