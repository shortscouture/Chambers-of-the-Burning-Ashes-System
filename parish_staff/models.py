from django.db import models
from accounts.models import CustomUser
# Create your models here.
class ChatLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Links to Django users
    message = models.TextField()  # User's message
    response = models.TextField()  # Bot's response
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"