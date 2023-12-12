from django.conf import settings  # import the settings file


def env_variables(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {"APP_ENV": settings.APP_ENV}
