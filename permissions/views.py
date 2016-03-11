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

from django.utils.translation import ugettext as _
from django.contrib.auth.models import Permission

from rest_framework import viewsets, permissions

from permissions.services import APIPermissionClassFactory

from permissions.serializers import PermissionSerializer


# Create permission class
PermissionPermission = APIPermissionClassFactory(
    name='PermissionPermission',
    permission_configuration={
        'base': {
            'list': True
        },
        'instance': {
            'retrieve': 'users.view_permission'
        }
    }
)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ :members: """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = (PermissionPermission, )
