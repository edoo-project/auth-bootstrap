# -*- coding: utf-8 -*-
"""
"""

__version__ = '0.1.0'
__author__ = 'Samuel Chávez <me@samuelchavez.com>'
__date__ = '04 January 2014'
__copyright__ = 'Copyright (c) 2012-2014 Samuel Chávez'
__license__ = 'THE LICENSE'
__status__ = 'development'
__docformat__ = 'reStructuredText'

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from rest_framework import serializers

from utils import services as utilities

from django.conf import settings

from permissions.serializers import PermissionSerializer

from users.models import PasswordRetrievalEvent
from users.services import (
    make_password_recovery_token,
    make_random_password)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    def _send_invitation(self, request, password_retrieval_event):
        utilities.send_multipart_email(
            _(u"¡Has sido invitado a Edoo! y tu nueva cuenta ha sido creada."),
            'email/welcome.html',
            {
                'user': password_retrieval_event.user,
                'first_config_link': '%s%s%s' % (
                    settings.FRONTEND_APP_URL,
                    '#/user/first-config/',
                    password_retrieval_event.token
                )
            },
            password_retrieval_event.user,
            request)

    def process_new_user(self, request, force_invite=False, commit=True):
        """
        Looks for a user, or creates a new one based on the form data given.

        :param commit: default True, checks if the algorithm should persist \
        if needed.
        """

        # The only way that the user could be created is if the srlzr is valid
        could_create = self.is_valid()

        # Fetch by email, if there is already one user with that email...
        email = self.data.get('email')
        users = User.objects.filter(email=email)

        # If the user already exists
        if users:
            user = users[0]

            # If forced to invite the user
            if force_invite:

                # Check if there are non-consumed password retrieval events
                user_retrieval_events = user.passwordretrievalevent_set.filter(
                    is_consumed=False)

                # If so
                if user_retrieval_events:

                    # Choose one
                    password_retrieval_event = user_retrieval_events[0]

                else:
                    # Generate new retrieval event for password recovery
                    new_token = make_password_recovery_token()
                    password_retrieval_event = PasswordRetrievalEvent(
                        user=user,
                        token=new_token)

                    # Save the retrieval event
                    password_retrieval_event.save()

                # Send invitaiton email
                self._send_invitation(
                    request,
                    password_retrieval_event)

            # Return it and advice that it has not been created
            return (user, False)
        else:

            # Check if a new user could be created. The only way that it cannot
            # happen is if there is not a user with the given username, but
            # there is a user with the given email.
            if could_create:

                new_user = User(
                    name=self.data.get('name'),
                    phone=self.data.get('phone'),
                    email=email)

                if commit:

                    # Save user
                    new_user.save()

                    # TODO: Permissions
                    # new_user.grant(perm="users.edit_basic_info", obj=)

                    # Generate retrieval event for password recovery
                    new_token = make_password_recovery_token()
                    password_retrieval_event = PasswordRetrievalEvent(
                        user=new_user,
                        token=new_token)

                    # Save entities
                    password_retrieval_event.save()

                    # Send invitaiton email
                    self._send_invitation(
                        request,
                        password_retrieval_event)

                return (new_user, True)

            return (None, False)

    class Meta:
        model = User

        fields = (
            'id',
            'name',
            'email',
            'phone')


class UserWithPermissionsSerializer(serializers.ModelSerializer):
    """
    Unfrotunately this serializer is needed. If not, every time user is
    editted, welcome need to send password as data parameter.
    """
    # user_permissions = PermissionSerializer(many=True, read_only=False)

    class Meta:
        model = User

        fields = (
            'id',
            'name',
            'email',
            'phone',
            'user_permissions')


class FirstConfigUserSerializer(serializers.ModelSerializer):
    """
    Unfrotunately this serializer is needed. If not, every time user is
    editted, welcome need to send password as data parameter.
    """
    class Meta:
        model = User

        fields = (
            'id',
            'name',
            'email',
            'phone',
            'password')

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class PasswordRetrievalEventSerializer(serializers.ModelSerializer):
    """ :members: """

    user = FirstConfigUserSerializer(many=False, read_only=False)
    """ Custom serializer for user relation. """

    class Meta:
        model = PasswordRetrievalEvent
