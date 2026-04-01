"""
Cozy Corner views.
"""
import json
import random
import re
import uuid
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Profile, Habit, HabitCompletion, JournalEntry
from .forms import SignupForm, LoginForm, ProfileForm, HabitForm

# Course topics (Khan Academy style)
COURSE_TOPICS = {
    'math': ['Fractions', 'Algebra', 'Geometry', 'Statistics'],
    'history': ['Declaration of Independence', 'War of 1812', 'Civil Rights Movement', 'World History'],
    'science': ['Cells', 'Energy', 'Physics Basics', 'Climate and Earth Science'],
    'reading': ['Reading Comprehension', 'Essay Writing', 'Grammar and Editing', 'Literary Analysis'],
}

# Dumpling responses for chat (kept short and comforting)
DUMPLING_RESPONSES = [
    "I'm here with you. Small steps still count.",
    "Take your time — learning isn't a race.",
    "You're doing better than you might think.",
    "It's okay to rest. That counts too.",
    "Want to try one tiny next step together?",
    "I'm rooting for you. One thing at a time.",
    "Your effort matters more than perfection.",
    "That takes courage. I'm glad you said it.",
]

# If the user mentions harm, never agree — redirect gently
HARMFUL_PATTERNS = re.compile(
    r'\b('
    r'kill\s*(myself|me)|suicid|self[\s-]*harm|hurt\s*(myself|me)|'
    r'end\s*it\s*all|don\'?t\s*want\s*to\s*live|want\s*to\s*die'
    r')\b',
    re.IGNORECASE,
)


def _ensure_guest_user(request):
    """Log in a session-bound guest so the app works without signup."""
    if request.user.is_authenticated:
        return
    guest_id = request.session.get('guest_user_id')
    if guest_id:
        try:
            user = User.objects.get(pk=guest_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return
        except User.DoesNotExist:
            del request.session['guest_user_id']
    username = f'guest_{uuid.uuid4().hex[:12]}'
    user = User.objects.create_user(username=username, password=uuid.uuid4().hex)
    user.set_unusable_password()
    user.save()
    Profile.objects.create(user=user, display_name='Guest')
    request.session['guest_user_id'] = user.pk
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')


def home(request):
    """Home page — guests enter automatically."""
    _ensure_guest_user(request)
    return render(request, 'core/home.html')


def signup_view(request):
    """Sign up - no email required. Guests can upgrade from a guest session."""
    if request.user.is_authenticated and not request.user.username.startswith('guest_'):
        return redirect('core:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            if request.session.get('guest_user_id'):
                del request.session['guest_user_id']
            if request.user.is_authenticated:
                logout(request)
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    """Login with username and password."""
    if request.user.is_authenticated and not request.user.username.startswith('guest_'):
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
                if request.session.get('guest_user_id'):
                    del request.session['guest_user_id']
                if request.user.is_authenticated:
                    logout(request)
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
    habit = Habit.objects.prefetch_related('completions').get(pk=pk)
    streak = _habit_streak(habit)
    completed_today = today in {c.date for c in habit.completions.filter(completed=True)}
    wants_json = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in (request.headers.get('Accept') or '')
    )
    if wants_json:
        return JsonResponse({
            'ok': True,
            'streak': streak,
            'completed_today': completed_today,
        })
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


def _dumpling_reply(message):
    """Supportive, short reply; never affirms harmful intent."""
    msg = (message or '').strip()
    if not msg:
        return "I'm here when you're ready. 🥟"
    if HARMFUL_PATTERNS.search(msg):
        return (
            "I'm really glad you reached out. I can't help with anything unsafe — "
            "please talk to a trusted adult, counselor, or call or text 988 (US) for crisis support. "
            "You deserve care and real help."
        )
    # Short, kind responses (max ~2 sentences)
    reply = random.choice(DUMPLING_RESPONSES)
    if len(reply) > 220:
        reply = reply[:217].rsplit(' ', 1)[0] + '…'
    return reply


@login_required
@require_http_methods(['POST'])
def chat_message_view(request):
    """Get dumpling response (AJAX)."""
    data = json.loads(request.body)
    msg = data.get('message', '').strip()
    reply = _dumpling_reply(msg)
    return JsonResponse({'reply': reply})


def _build_study_pack(topic):
    """Simple explanation + 3–5 quiz items for any topic (no external API)."""
    t = topic.strip()[:200] or 'your topic'
    explanation = (
        f"Here is a gentle start on “{t}.” Write one sentence in your own words about what it means to you. "
        f"Then add one new fact or idea. Revisit it tomorrow — short, repeated visits help more than one long cram."
    )
    questions = [
        {
            'q': f"What is one real-life example of {t}?",
            'options': ['Something you have seen or experienced', 'Only fictional stories', 'Ignore examples'],
            'correct': 0,
        },
        {
            'q': f"How could you check your understanding of {t}?",
            'options': ['Explain it aloud in one minute', 'Never review', 'Skip practice'],
            'correct': 0,
        },
        {
            'q': f"What is a small step to learn more about {t}?",
            'options': ['Read or watch for 10 minutes', 'Give up', 'Avoid the topic'],
            'correct': 0,
        },
        {
            'q': f"Why might {t} matter to you or your goals?",
            'options': ['It connects to something I care about', 'It never matters', 'Unknown'],
            'correct': 0,
        },
        {
            'q': f"If {t} feels hard, what helps most?",
            'options': ['Break it into smaller pieces', 'Only big pushes', 'Avoid thinking about it'],
            'correct': 0,
        },
    ]
    random.shuffle(questions)
    return explanation, questions[: random.randint(3, 5)]


@login_required
def study_view(request):
    """Topic-based study workspace with gentle practice."""
    return render(request, 'core/study.html')


@login_required
@require_http_methods(['POST'])
def study_generate_view(request):
    """Return explanation + quiz questions for a topic (JSON)."""
    data = json.loads(request.body)
    topic = (data.get('topic') or '').strip()
    if len(topic) < 2:
        return JsonResponse({'error': 'Please enter a topic (at least a couple of words).'}, status=400)
    explanation, questions = _build_study_pack(topic)
    return JsonResponse({'explanation': explanation, 'questions': questions, 'topic': topic})


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
