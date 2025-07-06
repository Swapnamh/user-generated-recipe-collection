from django.core.mail import send_mail
from .models import NewsletterSubscriber

def send_recipe_created_email(to_email, recipe_title):
    subject = "Your Recipe Has Been Created!"
    message = f"Congratulations! Your recipe '{recipe_title}' has been successfully created and published."
    from_email = 'swapnamh17@gmail.com'  # must match EMAIL_HOST_USER
    send_mail(subject, message, from_email, [to_email], fail_silently=False)


def send_recipe_purchase_email(to_email, buyer_name, recipe_title):
    subject = "Your Recipe Was Purchased!"
    message = f"{buyer_name} has purchased your recipe '{recipe_title}'."
    from_email = 'swapnamh17@gmail.com'  # your Gmail used in EMAIL_HOST_USER
    recipient_list = [to_email]
    
    print("Sending purchase email to:", to_email)  # DEBUG
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def send_recipe_rated_email(to_email, rater_name, recipe_title, rating_value):
    subject = "Your Recipe Has Been Rated!"
    message = f"{rater_name} has rated your recipe '{recipe_title}' with a score of {rating_value}."
    from_email = 'swapnamh17@gmail.com'
    send_mail(subject, message, from_email, [to_email], fail_silently=False)

def send_recipe_deleted_email(to_email, recipe_title, username):
    subject = "Recipe Deleted Successfully"
    message = f"Hi {username},\n\nYour recipe titled '{recipe_title}' has been successfully deleted from your account."
    from_email = 'swapnamh17@gmail.com'
    send_mail(subject, message, from_email, [to_email], fail_silently=False)

def send_recipe_published_email(to_email, recipe_title):
    subject = "Your Recipe Has Been Published!"
    message = f"Congratulations! Your recipe '{recipe_title}' has been published."
    send_mail(subject, message, "noreply@yourdomain.com", [to_email], fail_silently=False)

def send_newsletter(subject, message):
    subscribers = NewsletterSubscriber.objects.all()
    recipient_list = [sub.email for sub in subscribers]
    print("Subscribers to email:", recipient_list)  # Debug print

    if recipient_list:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print("Email sent successfully")
    else:
        print("No subscribers to send email to")

def send_weekly_newsletter():
    subject = "Weekly Recipes from Recipe Hub 🍽️"
    message = "Hi! Here are this week's delicious recipes and cooking tips. Enjoy!"
    send_newsletter(subject, message)
