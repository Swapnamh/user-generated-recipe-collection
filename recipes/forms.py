from django import forms
from .models import Recipe, RecipeRating
from .models import  Category
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'status', 'price', 'is_for_sale', 'category','video']
        widgets = {
            'category': forms.CheckboxSelectMultiple(),
            #'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_for_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        #self.fields['category'].empty_label = "Select a category"
        self.fields['image'].required = True  # Make image mandatory
    #class Meta:
    #    model = Recipe
     #   fields = ['title', 'description', 'image', 'status', 'price', 'is_for_sale', 'category']
      #  widgets = {
       #     'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter recipe details...'}),
        #    'is_for_sale': forms.CheckboxInput(),
         #   'category' : forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select a Category"),
            #'category': forms.Select(attrs={'class': 'category-select'}),
        #}
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("Please upload a photo.")
        return image
        
        
class RecipeRatingForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_pic']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].required = False  # ✅ Set to optional here


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'}))
