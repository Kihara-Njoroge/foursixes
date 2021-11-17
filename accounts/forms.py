from django import forms
from django.contrib.auth import get_user_model
from cuser.forms import UserCreationForm
from .models import Address

class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ("first_name", "last_name", "phno",
                  "email", "password1", "password2")
        model = get_user_model()

class AddressCreationForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name','phone_no', 'town', 'estate', 'apartment', 'primary']
