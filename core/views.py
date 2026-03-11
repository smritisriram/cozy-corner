"""
Cozy Corner views.
"""
import json
import random
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Habit, HabitCompletion, JournalEntry
from .forms import SignupForm, LoginForm, ProfileForm, HabitForm

# Course topics (Khan Academy style)
COURSE_TOPICS = {
    'math': ['Fractions', 'Algebra', 'Geometry', 'Statistics'],
    'history': ['Declaration of Independence', 'War of 1812', 'Civil Rights Movement', 'World History'],
    'science': ['Cells', 'Energy', 'Physics Basics', 'Climate and Earth Science'],
    'reading': ['Reading Comprehension', 'Essay Writing', 'Grammar and Editing', 'Literary Analysis'],
}

# Dumpling responses for chat
DUMPLING_RESPONSES = [
    "That's a great question! Take your time — learning happens at your own pace.",
    "I'm here for you. Remember, small steps still count as progress.",
    "You're doing better than you might think. Keep going!",
    "It's okay to take breaks. Rest is part of the process.",
    "I believe in you! What would help you feel more confident?",
    "Let's break this down into smaller pieces. What part feels hardest?",
    "You've got this. I'm rooting for you!",
    "Feeling overwhelmed is normal. Let's focus on just one thing at a time.",
    "Your effort matters. Progress over perfection.",
    "I'm proud of you for reaching out. That takes courage.",
]


def home(request):
    """Home page - redirect to signup if not logged in."""
    if not request.user.is_authenticated:
        return redirect('core:signup')
    return render(request, 'core/home.html')


def signup_view(request):
    """Sign up - no email required."""
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    """Login with username and password."""
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('core:home')
            form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Log out."""
    logout(request)
    return redirect('core:home')


@login_required
def courses_view(request):
    """Study courses."""
    return render(request, 'core/courses.html', {'topics': COURSE_TOPICS})


@login_required
def course_topics_view(request, subject):
    """Course topics for a subject."""
    topics = COURSE_TOPICS.get(subject, [])
    subject_names = {'math': 'Math', 'history': 'History / Social Studies', 'science': 'Science', 'reading': 'Reading & Writing'}
    return render(request, 'core/course_topics.html', {
        'subject': subject,
        'subject_name': subject_names.get(subject, subject),
        'topics': topics,
    })


@login_required
def exams_view(request):
    """Practice exams setup."""
    return render(request, 'core/exams.html')


@login_required
def exam_active_view(request):
    """Active exam - uses client-side JS for timer and questions."""
    return render(request, 'core/exam_active.html')


@login_required
@require_http_methods(['POST'])
def exam_complete_view(request):
    """Record exam completion."""
    try:
        profile = request.user.profile
        profile.exams_completed += 1
        profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user, display_name=request.user.username, exams_completed=1)
    return JsonResponse({'ok': True})


@login_required
def habits_view(request):
    """Habit tracker."""
    habits = list(request.user.habits.prefetch_related('completions').all())
    today = date.today()
    completions_by_habit = {h.id: {c.date for c in h.completions.filter(completed=True)} for h in habits}

    for h in habits:
        h.streak = _habit_streak(h)
        h.completed_today = today in completions_by_habit.get(h.id, set())

    # Calendar: last 14 days
    calendar_days = []
    d = today
    for _ in range(14):
        any_completed = any(d in completions_by_habit.get(h.id, set()) for h in habits)
        calendar_days.append({'label': d.day, 'completed': any_completed, 'today': d == today})
        d -= timedelta(days=1)
    calendar_days.reverse()

    return render(request, 'core/habits.html', {'habits': habits, 'calendar_days': calendar_days})


@login_required
@require_http_methods(['POST'])
def habit_add_view(request):
    """Add a habit."""
    form = HabitForm(request.POST)
    if form.is_valid():
        habit = form.save(commit=False)
        habit.user = request.user
        habit.save()
        return redirect('core:habits')
    return redirect('core:habits')


@login_required
@require_http_methods(['POST'])
def habit_toggle_view(request, pk):
    """Toggle habit completion for today."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()
    comp, created = HabitCompletion.objects.get_or_create(habit=habit, date=today, defaults={'completed': True})
    if not created:
        comp.delete()
    return redirect('core:habits')


@login_required
@require_http_methods(['POST'])
def habit_delete_view(request, pk):
    """Delete a habit."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    habit.delete()
    return redirect('core:habits')


@login_required
def journal_view(request):
    """Cozy journal."""
    entries = request.user.journal_entries.order_by('-created_at')
    return render(request, 'core/journal.html', {'entries': entries})


@login_required
def journal_entry_view(request, pk=None):
    """View or create journal entry."""
    if pk:
        entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    else:
        entry = JournalEntry.objects.create(user=request.user)
        return redirect('core:journal_entry', pk=entry.pk)
    entries = request.user.journal_entries.order_by('-created_at')
    return render(request, 'core/journal_entry.html', {'entry': entry, 'entries': entries})


@login_required
@require_http_methods(['POST'])
def journal_save_view(request, pk):
    """Save journal entry content (AJAX)."""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    data = json.loads(request.body)
    entry.content = data.get('content', '')
    entry.save()
    return JsonResponse({'ok': True})


@login_required
def chat_view(request):
    """Dumpling chat."""
    return render(request, 'core/chat.html')


@login_required
@require_http_methods(['POST'])
def chat_message_view(request):
    """Get dumpling response (AJAX)."""
    data = json.loads(request.body)
    msg = data.get('message', '').strip()
    reply = random.choice(DUMPLING_RESPONSES) if msg else "I'm here when you're ready to chat!"
    return JsonResponse({'reply': reply})


@login_required
def account_view(request):
    """Account settings."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, display_name=request.user.username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('core:account')
    else:
        form = ProfileForm(instance=profile, initial={'name': profile.display_name})

    # Stats
    habits = request.user.habits.prefetch_related('completions').all()
    max_streak = 0
    for h in habits:
        streak = _habit_streak(h)
        if streak > max_streak:
            max_streak = streak

    return render(request, 'core/account.html', {
        'form': form,
        'profile': profile,
        'habit_streak': max_streak,
        'journal_count': request.user.journal_entries.count(),
    })


def _habit_streak(habit):
    """Calculate current streak for a habit."""
    completions = {c.date: True for c in habit.completions.filter(completed=True)}
    today = date.today()
    streak = 0
    d = today
    for _ in range(365):
        if completions.get(d):
            streak += 1
        elif streak > 0:
            break
        d -= timedelta(days=1)
    return streak
