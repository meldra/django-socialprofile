"""Django Views for the socialprofile module"""
from django.shortcuts import render_to_response
from django.db import IntegrityError
from django.template import RequestContext
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from forms import SocialProfileForm
from django.views.generic import TemplateView
import logging

LOGGER = logging.getLogger(name='socialprofile')

def index(request):
    """
    Main site page page.

    url: /
    
    template : templates/index.html
    """

    LOGGER.debug('indexpage')

    response_data = {}

    return render_to_response('index.html', response_data, context_instance=RequestContext(request))


def select_view(request):
    """
    Lets users choose how they want to request access.

    url: /select
    
    template : templates/select.html
    """

    LOGGER.debug('selectpage')

    nextPage = request.GET.get('next', '/')

    response_data = {'next': nextPage}

    return render_to_response('select.html', response_data, context_instance=RequestContext(request))


def profile_view(request):
    """
    Profile View Page

    url: /

    template : templates/profile.html
    """

    LOGGER.debug('profileviewpage')

    form = SocialProfileForm(user=request.user) # Pass in User to Pre-Populate with Current Values

    response_data = {'form': form}

    return render_to_response('profile.html', response_data, context_instance=RequestContext(request))

@login_required
def profile_edit(request):
    """
    Profile Editing Page

    url: /

    template : templates/profile_edit.html
    """

    LOGGER.debug('profileeditpage')

    if request.method == 'POST': # If the form has been submitted...
        form = SocialProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = request.user
            form.clean()
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            profile = user.social_profile
            profile.gender = form.cleaned_data['gender']
            profile.url = form.cleaned_data['url']
            profile.image_url = form.cleaned_data['image_url']
            profile.description = form.cleaned_data['description']
            try:
                user.save()
                profile.save()
            except IntegrityError:
                form = SocialProfileForm()
                form._errors = {'username': [u'Your chosen username was not unique.'], }

            messages.add_message(request, messages.INFO, 'Your profile has been updated.')

            if form.cleaned_data.has_key('returnTo'):
                return HttpResponseRedirect(form.cleaned_data['returnTo'])

    else:
        form = SocialProfileForm(user=request.user) # Pass in User to Pre-Populate with Current Values

    response_data = {'form': form}

    return render_to_response('profile_edit.html', response_data, context_instance=RequestContext(request))


class DeleteView(TemplateView):
    """
    Account Delete Confirm Modal View

    url: /delete

    template : templates/delete_success.html
    """
    template_name = "delete_account_modal.html"


@login_required
def delete_action_view(request):
    """
    Account Delete Action view

    url: /delete/action

    template : templates/delete_success.html
    """

    LOGGER.debug('deletepage')

    #    if request.method == 'POST': # If the form has been submitted...
    #        if request.POST.has_key('confirm'):
    user_to_delete = request.user
    logout(request)
    user_to_delete.delete()

    response_data = {}

    return render_to_response('delete_success.html', response_data, context_instance=RequestContext(request))
