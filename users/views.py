from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from .forms import CustomUserCreationForm, LoginForm
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import SetPasswordForm
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_str
from django.conf import settings
from .forms import PasswordChangeForm 
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']  # Make sure email is saved
            user.save()

            # ✅ Send welcome email
            send_welcome_email(user.email, user.username)
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('recipes:home')
    else:
        
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Send login email
            send_login_email(user)

            messages.success(request, 'Welcome Back to RECIPE HUB..!')
            return redirect('recipes:home')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    user = request.user  # Save before logging out

    # ✅ Send logout email
    if user.is_authenticated:
        send_logout_email(user)

    logout(request)
    messages.success(request, 'You have been logged out ')
    return redirect('recipes:home')

@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    profile_user = request.user
    profile = getattr(profile_user, 'profile', None)

    user_recipes = Recipe.objects.filter(author=profile_user).order_by('-created_at')

    purchased_recipes = Recipe.objects.filter(
        purchases__buyer=profile_user
    ).distinct().select_related('author')

    return render(request, 'recipes/user_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'user_recipes': user_recipes,
        'purchased_recipes': purchased_recipes,
    })

def send_welcome_email(to_email, username):
    subject = "Welcome to Recipe Hub!"
    message = f"Hi {username}, thank you for registering at Recipe Hub. Happy cooking!"
    from_email = 'swapnamh17@gmail.com'
    send_mail(subject, message, from_email, [to_email], fail_silently=False)

def send_login_email(user):
    subject = "Login Notification"
    message = f"Hi {user.username},\n\nYou have successfully logged in to your account."
    send_mail(subject, message, 'swapnamh17@gmail.com', [user.email], fail_silently=False)

def send_logout_email(user):
    subject = "Logout Notification"
    message = f"Hi {user.username},\n\nYou have successfully logged out of your account."
    send_mail(subject, message, 'swapnamh17@gmail.com', [user.email], fail_silently=False)


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "registration/password_reset_email.html"
                c = {
                    "email": user.email,
                    'domain': request.get_host(),
                    'site_name': 'Your Site Name',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                }
                email_body = render_to_string(email_template_name, c)
                send_mail(subject, email_body, 'from@example.com', [user.email], fail_silently=False)
            messages.success(request, "Password reset email has been sent.")
            return redirect("users:password_reset_done")
        else:
            messages.error(request, "No user is associated with this email address.")
    return render(request, "users/password_reset.html")


def password_reset_done(request):
    return render(request, "users/password_reset_done.html")

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    validlink = False
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('users:password_reset_complete')  # Or wherever you want
        else:
            form = SetPasswordForm(user)
    else:
        form = None

    return render(request, 'users/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink,
    })
   

def password_reset_complete(request):
    return render(request, "users/password_reset_complete.html")

