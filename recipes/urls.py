from django.urls import path
from . import views
from .views import test_email_view


app_name = 'recipes'

urlpatterns = [
    # Home and browsing
    path('', views.home, name='home'),
    #path('browse/', views.browse_recipes, name='browse_recipes'),
    #path('submit/', views.submit_recipe, name='submit_recipe'),
    path('recipes/', views.all_recipes, name='all_recipes'),
    path('contact/', views.contact_view, name='contact'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('subscribers/', views.subscriber_list, name='subscriber_list'),
    path('unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    
    path('recipe/<int:recipe_id>/buy/', views.buy_recipe, name='buy_recipe'),
    path('recipe/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipes/', views.all_recipes, name='all_recipes'),
    path('category/<int:category_id>/', views.category_recipes, name='category_recipes'),
    
    # Recipe CRUD operations
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    
    path('recipe/submit/', views.submit_recipe, name='submit_recipe'),
    path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    
    # New recipe creation and category views
    path('create/', views.create_recipe, name='create_recipe'),
    path('create-recipe/', views.create_recipe, name='create_recipe'),
    path('category/<int:category_id>/', views.category_recipes, name='category_recipes'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    #path('profile/edit/', views.edit_profile, name='edit_profile'),
    #path('profile/remove-photo/', views.delete_profile_pic, name='delete_profile_pic'),
    #path('profile/delete-pic/', views.delete_profile_pic, name='delete_profile_pic'),
    #path('drafts/', views.draft_recipes, name='draft_recipes'),
    #path('publish-draft/<int:recipe_id>/', views.publish_draft, name='publish_draft'),
    
    path('profile/<int:user_id>/', views.user_profile_view, name='user_profile'),

    path('user/<int:user_id>/recipes/', views.UserRecipesAllView.as_view(), name='user_recipes_all'),
    path('user/<int:user_id>/purchased/', views.PurchasedRecipesAllView.as_view(), name='purchased_recipes_all'),
    path('user/<int:user_id>/', views.user_profile_view, name='user_profile'),
   #path('user/<int:user_id>/drafts/', views.draft_recipes_all, name='draft_recipes_all'),
    path('user/<int:user_id>/recipes/', views.user_recipes_all, name='user_recipes_all'),
    path('user/<int:user_id>/purchased/', views.purchased_recipes_all, name='purchased_recipes_all'),


    path('test-email/', test_email_view, name='test_email'),


]