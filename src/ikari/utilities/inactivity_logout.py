# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout


class InactivityLogout(object):
    def process_request(self, request):
        """
        Auto log out the user if appropriate or update last activity in session
        """
        if not request.user.is_authenticated():
            return

        try:
            LOGOUT_DELAY = getattr(settings, 'AUTO_LOGOUT_DELAY', 7200)
            now = datetime.now()
            delta = timedelta(seconds=LOGOUT_DELAY)
            lastActivity = datetime.strptime(request.session['last_activity'], "%Y-%m-%d %H:%M:%S.%f")

            if (now - lastActivity) > delta:
                logout(request)
                request.session['FORCED_LOGOUT'] = True
                del request.session['last_activity']
                return
        except KeyError:
            pass
        request.session['last_activity'] = str(datetime.now())
