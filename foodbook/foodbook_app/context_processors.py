from datetime import timedelta
from django.utils import timezone

def session_expiry_time(request):
    if request.user.is_authenticated:
        # Calculate session expiry timestamp
        session_expiry = timezone.now() + timedelta(seconds=request.session.get_expiry_age())
        return {'session_expiry_timestamp': int(session_expiry.timestamp())}
    return {}
