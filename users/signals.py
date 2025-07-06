# users/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    subject = "You've Logged In!"
    message = f"Hi {user.username}, you just logged in to Recipe Hub."
    from_email = 'swapnamh17@gmail.com'
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
