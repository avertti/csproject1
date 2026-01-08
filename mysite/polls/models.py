import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Fix 4:
# from django.contrib.auth.hashers import make_password, check_password


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Flaw 4: Cryptographic Failure A02
    # Storing sensitive information in plaintext
    access_code = models.CharField(max_length=16, blank=True, null=True)
    # Fix 4: Use password hashing
    # access_code = models.CharField(max_length=120, blank=True, null=True)

    # def save(self, *args, **kwargs):
    #    if self.access_code:
    #        self.access_code = make_password(self.access_code)
    #    super().save(*args, **kwargs)

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
