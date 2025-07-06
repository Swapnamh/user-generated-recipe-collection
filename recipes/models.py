from django.db import models
#from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings 
from django.utils import timezone 
from django.db.models.signals import post_save
from django.dispatch import receiver

#from django.contrib.auth import get_user_model

#User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Recipe(models.Model):
    STATUS_CHOICES = [
        
        ('published', 'Published'),
    ]
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
    ]


    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_recipes'  # Custom related name
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to='recipe_images/',
        #blank=False,
        #null=False,
        default='recipe_images/default.jpg' )
    video = models.FileField(
        upload_to='recipe_videos/',
        blank=True,
        null=True,
        help_text="Upload an optional recipe video (MP4 only)"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    category =models.ManyToManyField(Category, related_name='recipes')
    is_for_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    #is_draft = models.BooleanField(default=False)
    
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return f"{settings.MEDIA_URL}recipe_images/default.jpg"

    def __str__(self):
        if self.pk:
            cats = ", ".join([c.name for c in self.category.all()])
        else:
            cats = "No Category"
        return f"{self.title} ({cats})"

    
    def average_rating(self):
        return self.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0

class RecipeRating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='recipe_ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('recipe', 'user')

class Purchase(models.Model):
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE,
        related_name='purchases')
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
         on_delete=models.CASCADE,
         related_name='purchases')

    purchased_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('recipe', 'buyer')

    def __str__(self):
        return f"{self.buyer.username} purchased {self.recipe.title}"



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_users')
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', default='profiles/default_profile.png')

    def __str__(self):
        return f"{self.user.username}'s Profile"



class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email