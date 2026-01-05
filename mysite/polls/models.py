import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = "pub_date"
    was_published_recently.boolean = True
    was_published_recently.short_description = "Published recently?"

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


# FLAW 4: A07:2021 - Identification and Authentication Failures
# Storing passwords in plain text
class UserAccount(models.Model):
    username = models.CharField(max_length=100, unique=True)
    # VULNERABLE: Password stored as plain text
    password = models.CharField(max_length=100)
    # FIX: Use Django's built-in User model with hashed passwords
    # from django.contrib.auth.models import User
    # Or use proper password hashing:
    # from django.contrib.auth.hashers import make_password, check_password
    # password = models.CharField(max_length=128)  # Store hashed password
    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)
    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.password)
    
    email = models.EmailField()
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
