from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Recipe, RecipeRating, Purchase
from .forms import RecipeForm, RecipeRatingForm
from users.models import User
from .models import Category
from .forms import RecipeForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from .models import Recipe, Category
from .utils import send_recipe_purchase_email
from django.contrib.auth import get_user_model
from users.models import UserProfile
from .forms import UserForm, UserProfileForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
from django.views.generic import ListView
from .forms import ContactForm
from .models import NewsletterSubscriber
from django.contrib.admin.views.decorators import staff_member_required
from .utils import send_recipe_created_email, send_recipe_purchase_email, send_recipe_rated_email,send_recipe_deleted_email,send_newsletter,send_weekly_newsletter 
from .forms import UserForm, UserProfileForm
User = get_user_model()
from django.contrib.auth.models import User
import markdown
import re

def home(request):
    query = request.GET.get('q', '').strip()
    
    recipes = Recipe.objects.filter(title__icontains=query) if query else Recipe.objects.all()
    users = User.objects.filter(username__icontains=query) if query else []

    # Update search history in session
    if query:
        history = request.session.get('search_history', [])
        if query not in history:
            history.insert(0, query)
            request.session['search_history'] = history[:5]
        request.session.modified = True

    context = {
        'featured_recipes': recipes[:6],
        'categories': Category.objects.all(),
        'query': query,
        'search_users': users,
        'search_mode': bool(query),
        'recipes_by_category': {
            category: category.recipes.all()[:3]
            for category in Category.objects.all()
        }
    }

    return render(request, 'recipes/home.html', context)

@login_required
def submit_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user

            if request.POST.get('submit_type') == 'publish':
                recipe.status = 'published'
                messages.success(request, 'Your recipe has been published!')
                request.user.send_recipe_created_email(recipe)
            else:
                recipe.status = 'draft'
                messages.info(request, 'Your recipe has been saved as draft.')

            recipe.save()
            form.save_m2m()
            print("Saved recipe:", recipe.title, "| Status:", recipe.status)

            return redirect('recipes:user_profile', user_id=request.user.id)
    else:
       initial_data = {}
       category_param = request.GET.get('category')
       if category_param:
           try:
               category_obj = Category.objects.get(name__iexact=category_param)
               initial_data['category'] = [category_obj]
           except Category.DoesNotExist:
               pass

    form = RecipeForm(initial=initial_data)
    return render(request, 'recipes/submit_recipe.html', {'form': form, 'selected_category': category_param})

def clean_description(text):
    if not text:
        return ''
    # Remove empty lines at start and end (lines containing only whitespace)
    return re.sub(r'^\s*\n+|\n+\s*$', '', text)


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.description = clean_description(recipe.description)
    user = request.user

    user_rating = None
    has_purchased = False

    # Only fetch user-specific info if authenticated
    if user.is_authenticated:
        user_rating = RecipeRating.objects.filter(recipe=recipe, user=user).first()
        has_purchased = Purchase.objects.filter(recipe=recipe, buyer=user).exists()

        if request.method == 'POST':
            if 'rating_submit' in request.POST:
                rating_form = RecipeRatingForm(request.POST, instance=user_rating)
                if rating_form.is_valid():
                    rating = rating_form.save(commit=False)
                    rating.recipe = recipe
                    rating.user = user
                    rating.save()
                    messages.success(request, 'Your rating has been submitted!')

                    # Notify recipe author about rating
                    send_recipe_rated_email(
                        recipe.author.email,
                        user.username,
                        recipe.title,
                        rating.rating
                    )
                    return redirect('recipes:recipe_detail', recipe_id=recipe.id)

            elif 'buy_recipe' in request.POST:
                if not has_purchased and recipe.is_for_sale and recipe.author != user:
                    Purchase.objects.create(recipe=recipe, buyer=user)

                    # Notify recipe author about purchase
                    send_recipe_purchase_email(
                        to_email=recipe.author.email,
                        buyer_name=user.username,
                        recipe_title=recipe.title
                    )
                    messages.success(request, 'You have successfully purchased this recipe!')
                    return redirect('recipes:recipe_detail', recipe_id=recipe.id)
    else:
        # Handle POST attempt from anonymous user
        if request.method == 'POST':
            messages.warning(request, 'You need to be logged in to rate or purchase this recipe.')
            return redirect('login')

    rating_form = RecipeRatingForm(instance=user_rating)

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'has_purchased': has_purchased,
    })


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe_obj = form.save(commit=False)  # Save the object but don’t commit yet
            recipe_obj.save()                     # Now save to DB
            form.save_m2m()                       # Save many-to-many relationships
            messages.success(request, 'Your recipe has been updated!')
            return redirect('recipes:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/edit_recipe.html', {'form': form, 'recipe': recipe})

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Only allow author to delete
    if recipe.author != request.user:
        messages.error(request, "You are not authorized to delete this recipe.")
        return redirect('recipes:recipe_detail', recipe_id=recipe_id)

    if request.method == 'POST':
        recipe_title = recipe.title # Store title before deletion
        recipe.delete()

        # ✅ Send email to the user
        send_recipe_deleted_email(
            to_email=request.user.email,
            recipe_title=recipe_title,
            username=request.user.username
        )
        
        messages.success(request, 'Your recipe has been deleted!')
        return redirect('recipes:user_profile', user_id=request.user.id)

    # Render a confirmation page if you want
    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})


@login_required
def create_recipe(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('recipes:user_profile', user_id=request.user.id)
        
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            
            # Set author
            recipe.author = request.user
            
            # Set status based on which button was clicked
            if 'publish' in request.POST:
                recipe.status = 'published'
            elif 'draft' in request.POST:
                recipe.status = 'draft'
            else:
                recipe.status = 'draft'  # Default to draft if somehow no button clicked
            
            recipe.save()          # Save to get primary key for M2M
            form.save_m2m()       # Save ManyToMany category relations
            
            # Optionally send email or show success message
            if 'publish' in request.POST:
                messages.success(request, 'Your recipe has been published successfully!')
                return redirect('recipes:category_recipes', recipe.category.first().id if recipe.category.exists() else None)
            else:
                messages.success(request, 'Your recipe has been saved as draft.')
                return redirect('recipes:user_drafts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipeForm()
    
    return render(request, 'recipes/create_recipe.html', {'form': form})



class UserRecipesAllView(ListView):
    model = Recipe
    template_name = 'recipes/user_recipes_all.html'  # create this template
    context_object_name = 'recipes'
    paginate_by = 12  # optional pagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Recipe.objects.filter(author__id=user_id).order_by('-created_at')


class PurchasedRecipesAllView(ListView):
    model = Recipe
    template_name = 'recipes/purchased_recipes_all.html'  # create this template
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        # Assuming you have a Purchase model linking users and recipes they bought
        return Recipe.objects.filter(purchase__buyer__id=user_id).order_by('-purchase__date')
        
    
def category_recipes(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    recipes = Recipe.objects.filter(category__in=[category])

    return render(request, 'recipes/category_recipe.html', {
        'category': category,
        'recipes': recipes
    })

def all_recipes(request):
    recipes = Recipe.objects.filter(status='published')
    return render(request, 'recipes/all_recipes.html', {'recipes': recipes})
    


@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    draft_recipes  = None
    #purchased_recipes = None
    # Drafts only for profile owner
    if request.user == user:
        draft_recipes = Recipe.objects.filter(author=user, status='draft').order_by('-created_at')
        #purchased_recipes = Recipe.objects.filter(purchased_by=user).order_by('-created_at')  # Assuming purchased_by M2M or FK
    
     # Only published recipes should be shown to everyone
    user_recipes = Recipe.objects.filter(author=user, status='published').order_by('-created_at')

    # Published recipes (exclude drafts)
    #published_recipes = Recipe.objects.filter(author=user, status='published').order_by('-created_at')
    #published_count = published_recipes.count()

    profile, created = UserProfile.objects.get_or_create(user=user)  # ← this is key
    context = {
      'profile_user': user,
      'draft_recipes': draft_recipes,
      'user_recipes': user_recipes,
      'profile': profile,
      
    }
    print("Logged-in user:", request.user.username)
    print("Viewing profile of:", user.username)
    print("Drafts count:", draft_recipes.count() if draft_recipes else 0)
    print("Published count:", user_recipes.count())

    return render(request, 'recipes/user_profile.html', context)




@login_required
def buy_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if recipe.is_for_sale:
        if not Purchase.objects.filter(user=request.user, recipe=recipe).exists():
            Purchase.objects.create(user=request.user, recipe=recipe)
            messages.success(request, 'Recipe purchased successfully!')
        else:
            messages.info(request, 'You have already purchased this recipe.')
    return redirect('recipes:recipe_detail', recipe_id=recipe.id)

@login_required
def rate_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.recipe = recipe
            rating.save()
            messages.success(request, 'Rating added successfully!')
            return redirect('recipes:recipe_detail', recipe_id=recipe.id)
    else:
        form = RatingForm()
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe, 'rating_form': form})



@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            cropped_image = request.FILES.get('cropped_profile_pic')
            if cropped_image:
                try:
                    cropped_image.seek(0)  # Reset pointer to start
                    image_temp = Image.open(cropped_image)

                    if image_temp.mode in ("RGBA", "LA") or (image_temp.mode == "P" and "transparency" in image_temp.info):
                        background = Image.new("RGB", image_temp.size, (255, 255, 255))
                        background.paste(image_temp, mask=image_temp.split()[3])
                        image_temp = background
                    else:
                        image_temp = image_temp.convert("RGB")

                    image_io = BytesIO()
                    image_temp.save(image_io, format='JPEG')
                    image_io.seek(0)  # Reset pointer after save

                    image_file = InMemoryUploadedFile(
                        image_io,
                        'ImageField',
                        f"{user.username}_cropped.jpg",
                        'image/jpeg',
                        image_io.getbuffer().nbytes,
                        None
                    )
                    profile.profile_pic = image_file
                except Exception as e:
                    messages.error(request, f"Error processing image: {e}")

            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('recipes:user_profile', user_id=user.id)
        else:
            if user_form.errors:
                messages.error(request, f"User form error: {user_form.errors.as_text()}")
            if profile_form.errors:
                messages.error(request, f"Profile form error: {profile_form.errors.as_text()}")

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'recipes/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def delete_profile_pic(request):
    profile = request.user.profile_users
    if profile.profile_pic:
        # Delete the file from storage
        profile.profile_pic.delete(save=False)
        # Clear the field in database
        profile.profile_pic = None
        profile.save()
        messages.success(request, 'Profile picture removed successfully.')
    else:
        messages.warning(request, 'No profile picture to remove.')

    return HttpResponseRedirect(reverse('recipes:edit_profile'))

@login_required
def draft_recipes(request):
    drafts = Recipe.objects.filter(author=request.user, status='draft')
    return render(request, 'recipes/draft_recipes.html', {'drafts': drafts})

@login_required
def publish_draft(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        recipe.status = 'published'
        recipe.save()
        messages.success(request, 'Draft published successfully!')
        return redirect('recipes:user_profile', user_id=request.user.id)  # Or redirect where you want
    else:
        return render(request, 'recipes/publish_draft.html', {'recipe': recipe})

def test_email_view(request):
    send_mail(
        subject='Test Email from Django',
        message='This is a test email to verify SMTP setup.',
        from_email='noreply@yourdomain.com',
        recipient_list=['your_email@gmail.com'],  # Use a real email here
        fail_silently=False,
    )
    return HttpResponse("Test email sent!")

@login_required
def publish_draft_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if recipe.status == 'draft':
        recipe.status = 'published'
        recipe.save()
        messages.success(request, f"Recipe '{recipe.title}' published successfully.")

        # ✅ Send email notification
        send_recipe_published_email(request.user.email, recipe.title)

    return redirect('recipes:user_profile', user_id=request.user.id)

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

@login_required
def draft_recipes_all(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user:
        return redirect('recipes:user_profile', user_id=user.id)
    draft_recipes = Recipe.objects.filter(author=user, is_draft=True)
    return render(request, 'recipes/draft_recipes_all.html', {'draft_recipes': draft_recipes, 'profile_user': user})

@login_required
def user_recipes_all(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    #user_recipes = Recipe.objects.filter(author=profile_user)
    # ✅ Use the related_name to get authored recipes
    Recipe.objects.filter(author=profile_user, status='published').order_by('-created_at')

    return render(request, 'recipes/user_recipes_all.html', {
        'profile_user': profile_user,
        'user_recipes': user_recipes,
    })

@login_required
def purchased_recipes_all(request, user_id):
    user = get_object_or_404(User, id=user_id)
    purchased_recipes = user.purchased_recipes.all()
    return render(request, 'recipes/purchased_recipes_all.html', {'purchased_recipes': purchased_recipes, 'profile_user': user})

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def user_profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    user_recipes = Recipe.objects.filter(
        author=profile_user, status='published'
    ).order_by('-created_at')[:6]

    purchased_recipes = None

    # Show purchased recipes only if the logged-in user is viewing their own profile
    if request.user.is_authenticated and request.user == profile_user:
        purchased_recipes = Recipe.objects.filter(
            purchases__buyer=profile_user, status='published'
        ).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'user_recipes': user_recipes,
        'purchased_recipes': purchased_recipes,
    }
    return render(request, 'recipes/user_profile.html', context)

@login_required
def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                # Send confirmation email here
                subject = "Thanks for subscribing to Recipe Hub!"
                message = (
                    f"Hi,\n\nThank you for subscribing to Recipe Hub . "
                    "You'll start receiving our delicious recipes and updates soon!"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]

                try:
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    messages.success(request, "Thanks for subscribing! A confirmation email has been sent.")
                except Exception as e:
                    # If email fails, still show success but notify admin or log error
                    messages.warning(request, "Subscribed successfully but email could not be sent.")
                    print("Email sending error:", e)
            else:
                messages.info(request, "You are already subscribed.")
        else:
            messages.error(request, "Please enter a valid email.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def unsubscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                subscriber = NewsletterSubscriber.objects.get(email=email)
                subscriber.delete()
                messages.success(request, "You have successfully unsubscribed from the Recipe Hub.")
            except NewsletterSubscriber.DoesNotExist:
                messages.error(request, "This email is not subscribed.")
        else:
            messages.error(request, "Please enter a valid email address.")
        return redirect('recipes:unsubscribe_newsletter')  # Redirect back to unsubscribe page or any other page
    return render(request, 'recipes/unsubscribe_newsletter.html')  # Render unsubscribe form page



@staff_member_required
def subscriber_list(request):
    subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    return render(request, 'recipes/subscriber_list.html', {'subscribers': subscribers})


@login_required
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            subject = f"New Feedback Message from {name}"
            full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,  # FROM
                [settings.DEFAULT_FROM_EMAIL],  # TO (Admin email)
                fail_silently=False,
            )

            messages.success(request, 'Your Feedback has been sent successfully!')
            return redirect('recipes:home')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'recipes/contact.html')

def get_formatted_description(self):
    return markdown.markdown(self.description)