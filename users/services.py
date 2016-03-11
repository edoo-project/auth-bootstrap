# -*- coding: utf-8 -*-
"""
Miscelaneous user utility services for Edoo.
"""

__version__ = '0.1.0'
__author__ = 'Samuel Chávez <me@samuelchavez.com>'
__date__ = '25 November 2013'
__copyright__ = 'Copyright (c) 2012-2014 Samuel Chávez'
__license__ = 'THE LICENSE'
__status__ = 'development'
__docformat__ = 'reStructuredText'

from django.contrib.auth import get_user_model

User = get_user_model()


def make_random_password(length=10,
                         allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                       'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                       '123456789'):
    """
    Taken from:
    http://stackoverflow.com/questions/9480641/django-password-generator
    Based on: django.utils.crypto.get_random_string

    :rtype: string
    """
    return User.objects.make_random_password(length, allowed_chars)


def make_password_recovery_token():
    """
    :rtype: string (length=20)
    """
    return make_random_password(length=20)
