from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class UsersConfessions(models.Model):
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField("time of the post created")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="confessions")