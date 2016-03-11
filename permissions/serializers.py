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
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext as _

from rest_framework import serializers

from utils import services as utilities

from django.conf import settings

from users.models import PasswordRetrievalEvent
from users.services import (
    make_password_recovery_token,
    make_random_password)


class PermissionSerializer(serializers.ModelSerializer):
    """ :members: """

    class Meta:
        model = Permission
