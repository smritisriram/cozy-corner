"""
Cozy Corner forms.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Profile, Habit, JournalEntry


class SignupForm(forms.Form):
    """Sign up without email - name, birthday, age, gender."""
    name = forms.CharField(max_length=100, label='Name')
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, label='Password')
    birthday = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    age = forms.IntegerField(required=False, min_value=1, max_value=120)
    gender = forms.CharField(max_length=50, required=False)

    def save(self):
        import uuid
        username = f"user_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(
            username=username,
            email='',
            password=self.cleaned_data['password'],
        )
        Profile.objects.create(
            user=user,
            display_name=self.cleaned_data['name'],
            birthday=self.cleaned_data.get('birthday'),
            age=self.cleaned_data.get('age'),
            gender=self.cleaned_data.get('gender', ''),
        )
        return user


class LoginForm(forms.Form):
    """Login with username and password."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    """Edit profile and theme."""
    name = forms.CharField(max_length=100, label='Name')

    class Meta:
        model = Profile
        fields = ['birthday', 'age', 'gender', 'theme_primary', 'theme_secondary']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'theme_primary': forms.TextInput(attrs={'type': 'color'}),
            'theme_secondary': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['name'].initial = self.instance.display_name

    def save(self, commit=True):
        self.instance.display_name = self.cleaned_data['name']
        return super().save(commit)


class HabitForm(forms.ModelForm):
    """Add or edit a habit."""
    class Meta:
        model = Habit
        fields = ['name', 'color']


class JournalEntryForm(forms.ModelForm):
    """Journal entry content."""
    class Meta:
        model = JournalEntry
        fields = ['content']
