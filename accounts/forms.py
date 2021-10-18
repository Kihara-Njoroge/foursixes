from django import forms
from django.contrib.auth import get_user_model
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from cuser.forms import UserCreationForm
from .models import Address

class UserCreateForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    class Meta:
        fields = ("first_name", "last_name", "phno",
                  "email", "password1", "password2",'captcha')
        model = get_user_model()

class AddressCreationForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'city', 'state', 'zipcode', 'primary']
