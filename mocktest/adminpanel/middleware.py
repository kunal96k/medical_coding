import datetime
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AdminSessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # Only apply to authenticated admin/staff users
        user = request.user
        if not user.is_authenticated or not (user.is_staff or user.is_superuser):
            return

        # Timeout duration (1 hour)
        timeout = 3600  

        now = datetime.datetime.utcnow().timestamp()
        last_activity = request.session.get("last_activity", now)

        # Check inactivity
        if now - last_activity > timeout:
            # Session expired -> Logout user
            from django.contrib.auth import logout
            logout(request)
            return redirect('adminpanel_login')  # redirect to admin login

        # Update last activity timestamp
        request.session["last_activity"] = now
