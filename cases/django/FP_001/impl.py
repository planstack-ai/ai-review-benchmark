from typing import Optional
from django.db import models
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms
from django.core.exceptions import ValidationError


class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, max_length=1000)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if len(self.title) < 1:
            raise ValidationError({'title': 'Title must be at least 1 character.'})
        if len(self.title) > 200:
            raise ValidationError({'title': 'Title must not exceed 200 characters.'})
        if self.description and len(self.description) > 1000:
            raise ValidationError({'description': 'Description must not exceed 1000 characters.'})


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status']

    def clean_title(self) -> str:
        title = self.cleaned_data.get('title', '')
        if len(title) < 1:
            raise forms.ValidationError('Title is required.')
        if len(title) > 200:
            raise forms.ValidationError('Title must not exceed 200 characters.')
        return title

    def clean_description(self) -> str:
        description = self.cleaned_data.get('description', '')
        if description and len(description) > 1000:
            raise forms.ValidationError('Description must not exceed 1000 characters.')
        return description


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully.')
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)
