from django.shortcuts import redirect


def unauthenticated_user(view_func):
    """Decorator for checking user access to certain views"""

    def wrapper_func(request, *args, **kwargs):
        """Check authenticated user"""
        if request.user.is_authenticated:
            return redirect("landing")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
