from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


def my_logout(request, next_='/'):
    logout(request)
    # if ('next' in request.GET) and request.GET['next'].strip():
    #    next_=request.GET['next']

    return HttpResponseRedirect(next_)
