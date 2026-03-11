"""
Cozy Corner models.
"""
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Extended user profile - no email required."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    theme_primary = models.CharField(max_length=7, default='#8B9A7A')
    theme_secondary = models.CharField(max_length=7, default='#C4A77D')
    exams_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.display_name or self.user.username


class Habit(models.Model):
    """User habit for tracking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#8B9A7A')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HabitCompletion(models.Model):
    """Daily completion record for a habit."""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ['habit', 'date']

    def __str__(self):
        return f"{self.habit.name} - {self.date}"


class JournalEntry(models.Model):
    """Journal entry for creative writing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Entry {self.id} - {self.created_at.date()}"
