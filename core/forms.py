from django import forms
from .models import Task

# TaskForm for creating and editing tasks
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','status','deadline']