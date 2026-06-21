from .models import PWASetting


def pwa_settings(request):
    return {'pwa_settings': PWASetting.get_active()}
