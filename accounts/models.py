
from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from django.utils import timezone



class Profile(BaseModel):
    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100 , null=True , blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)



@receiver(post_save , sender = User)
def  send_email_token(sender , instance , created , **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance , email_token = email_token)
            email = instance.email
            send_account_activation_email(email , email_token)

    except Exception as e:
        print(e)


class Contact(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField(max_length=255, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    desc = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    

