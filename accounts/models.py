import uuid

from django.db import models
from django.core.exceptions import ValidationError
from cuser.models import AbstractCUser


def phone_validator(phno):
    errormsg = 'Enter a valid 10 digit phone number'
    try:
        if len(phno) != 10 or not phno.isdigit():
            raise ValidationError(errormsg)
    except:
        raise ValidationError(errormsg)
 

class User(AbstractCUser):
    phno = models.CharField(null=True, max_length=10, validators=[phone_validator])
    # users address related name = addresses
    # users wishlist related name = wlist
    # users cart related name = cart

    # to-dos
    # def get_primary_address(self):
    #     pass
    # search for given user's addresses where primary field is true
    # select 1st address and return

    # def set_primary_address(self, address):
    #     pass
    # search for given user's addresses where primary field is true
    # select 1st address and set primary field to false
    # then set current address as primary


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses', null=True)
    # ig django stores model name in lower case so address field might clash ..not sure
    address = models.CharField(max_length=250, null=False)
    city = models.CharField(max_length=50, null=False)
    state = models.CharField(max_length=50, null=False)
    zipcode = models.CharField(max_length=50, null=False)
    # primary field used to store the primaty/default address of user
    primary = models.BooleanField(blank=True, default=False)
