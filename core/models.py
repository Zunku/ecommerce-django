from django.contrib.auth.models import AbstractUser
from django.db import models
# Changin store custom to core. This is the core of our proyect, where all the apps will comunicate
# Extending user
# If you do this in middle of a proyect you will have errors with migrations, and will need to restart the database, so it's a best practice to start this class with pass at the begining of a proyect, despite you will not use it
class User(AbstractUser):
    # Adding a new field to the user model, to enable login with email
    email = models.EmailField(unique=True)