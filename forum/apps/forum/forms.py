from django.forms import ModelForm
from django.shortcuts import  render_to_response


from os.path import join as pjoin
from .models import UserProfile

class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ["posts", "user"]

