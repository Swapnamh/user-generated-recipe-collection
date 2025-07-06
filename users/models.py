from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core.mail import send_mail
from django.conf import settings
from django import forms
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth import get_user_model
#User = get_user_model()
from recipes.models import UserProfile

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)



class User(AbstractUser):
    pass
    email = models.EmailField(unique=True)
    objects = UserManager()

    

    def get_average_rating(self):
        from recipes.models import RecipeRating
        recipes = self.authored_recipes.all()
        if not recipes.exists():
            return 0
        total = 0
        count = 0
        for recipe in recipes:
            avg = recipe.average_rating()
            if avg:
                total += avg
                count += 1
        return total / count if count > 0 else 0

    def send_recipe_created_email(self, recipe):
        subject = 'Your recipe has been created!'
        message = f'Hello {self.username},\n\nYour recipe "{recipe.title}" has been successfully created.'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def send_recipe_purchased_email(self, recipe, buyer):
        subject = f'Your recipe "{recipe.title}" has been purchased!'
        message = f'Hello {self.username},\n\nYour recipe "{recipe.title}" has been purchased by {buyer.username}.'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Add this
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Add this
        related_query_name='user',
    )

    def get_recipes(self):
        """Get all recipes created by this user"""
        return self.authored_recipes.all()  # Using custom related_name
    
    def get_purchased_recipes(self):
        """Get all recipes purchased by this user"""
        return self.purchased_recipes.all()






