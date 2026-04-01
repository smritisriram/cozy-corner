"""
Template context processors.
"""
def profile(request):
    """Add profile and theme to template context."""
    ctx = {
        'profile': None,
        'theme_primary': '#8B9A7A',
        'theme_secondary': '#C4A77D',
        'is_guest': False,
    }
    if request.user.is_authenticated:
        ctx['is_guest'] = request.user.username.startswith('guest_')
        try:
            p = request.user.profile
            ctx['profile'] = p
            ctx['theme_primary'] = p.theme_primary
            ctx['theme_secondary'] = p.theme_secondary
        except Exception:
            pass
    return ctx
