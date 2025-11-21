from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Model to store tasks assigned to users
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Linked user
    title = models.CharField(max_length=200)  # Task title
    description = models.TextField(blank=True, null=True)  # Optional details
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed')
        ],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Created timestamp
    deadline = models.DateField(blank=True, null=True)  # Optional due date

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

