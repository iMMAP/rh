from django.shortcuts import redirect

def unauthenticated_user(view_func):
	"""Decorator for checking user access to certain views"""
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('index')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func
