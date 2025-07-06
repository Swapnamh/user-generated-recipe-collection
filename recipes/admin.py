from django.contrib import admin
from .models import Recipe, RecipeRating, Purchase
from .models import NewsletterSubscriber

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')  # Customize fields you want to see
    search_fields = ('email',)
    
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'is_for_sale', 'price', 'created_at')
    list_filter = ('status', 'is_for_sale')
    search_fields = ('title', 'description', 'author__username')

class RecipeRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('recipe__title', 'user__username')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'buyer', 'purchased_at')
    search_fields = ('recipe__title', 'buyer__username')

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeRating, RecipeRatingAdmin)
admin.site.register(Purchase, PurchaseAdmin)