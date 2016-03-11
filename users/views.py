# -*- coding: utf-8 -*-
"""
Application's views.
"""

__version__ = '0.1.0'
__author__ = 'Samuel Chávez <me@samuelchavez.com>'
__date__ = '18 January 2016'
__copyright__ = 'Copyright (c) 2012-2014 Samuel Chávez'
__license__ = 'THE LICENSE'
__status__ = 'development'
__docformat__ = 'reStructuredText'

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import (
    status,
    filters
)

from permissions.services import APIPermissionClassFactory

from users.models import (
    User,
    PasswordRetrievalEvent)

from users.serializers import (
    UserSerializer,
    FirstConfigUserSerializer,
    PasswordRetrievalEventSerializer,
    UserWithPermissionsSerializer)


# Create permission class
UserPermission = APIPermissionClassFactory(
    name='UserPermission',
    permission_configuration={
        'base': {
            'invite': 'users.add_user',
            'list': 'users.search_user'
        },
        'instance': {
            'retrieve': 'users.view_user',
            'update':  'users.change_user',
            'destroy': 'users.delete_user',
            'permission': {
                'GET': True,
                'PUT': 'users.change_user'
            }
        }
    }
)


class UserViewSet(viewsets.ModelViewSet):
    """ :members: """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('email', 'is_active')
    search_fields = ('email', 'name')

    permission_classes = (UserPermission, )

    def get_serializer_class(self):
        return UserSerializer

    @list_route(methods=['post'])
    def invite(self, request, pk=None):
        user_invite_serializer = UserSerializer(
            data=request.data)

        # Process user and check if it was already in our system
        user, created = user_invite_serializer.process_new_user(
            request,
            force_invite=True)

        if created:
            rstatus = status.HTTP_201_CREATED
        elif user:
            rstatus = status.HTTP_200_OK
        else:
            rstatus = status.HTTP_400_BAD_REQUEST

        return Response(UserSerializer(instance=user).data, status=rstatus)

    @detail_route(methods=['get', 'put'])
    def permission(self, request, pk):
        user = self.get_object()

        # Get all user permissions
        if request.method == 'GET':
            serialized_user = UserWithPermissionsSerializer(instance=user)
            return Response(serialized_user.data)

        # Update permissions
        elif request.method == 'PUT':
            serialized_user = UserWithPermissionsSerializer(
                instance=user,
                data=request.data,
                partial=True)

            # If incomming data is valid
            if serialized_user.is_valid():

                # Update
                serialized_user.save()

                # Response
                return Response(serialized_user.data)

            # Response errors
            return Response(
                serialized_user.errors,
                status.HTTP_412_PRECONDITION_FAILED)


class PasswordRetrievalEventTokenView(APIView):
    """ :members: """

    permission_classes = (permissions.AllowAny, )

    def get(self, request, token, format=None):
        # Fetch
        pwevent = get_object_or_404(
            PasswordRetrievalEvent.objects.all(),
            token=token)

        # Serialize
        pwevent_serializer = PasswordRetrievalEventSerializer(instance=pwevent)

        # Validation
        if not pwevent.is_consumed:

            return Response(pwevent_serializer.data)

        return Response({
            'details': _(u"Token expirado")
        }, status.HTTP_412_PRECONDITION_FAILED)

    def put(self, request, token, format=None):

        # Fetch
        pwevent = get_object_or_404(
            PasswordRetrievalEvent.objects.all(),
            token=token)

        # Validation
        if not pwevent.is_consumed:

            # User
            user = pwevent.user

            # Data serialization
            serialized_user = FirstConfigUserSerializer(
                user,
                data=request.data,
                partial=True)

            # If incomming data is valid
            if serialized_user.is_valid():

                # Update
                serialized_user.save()

                # Set password
                user.set_password(
                    serialized_user.validated_data.get('password'))

                # Save
                user.save()

                return Response(serialized_user.data)

        return Response({
            'details': _(u"Token expirado")
        }, status.HTTP_412_PRECONDITION_FAILED)


# def forgot_password(request, request_data):
