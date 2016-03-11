# -*- coding: utf-8 -*-
"""
Model layer of the application.
"""

__version__ = '0.1.0'
__author__ = 'Samuel Chávez <me@samuelchavez.com>'
__date__ = '4 January 2016'
__copyright__ = 'Copyright (c) 2012-2014 Samuel Chávez'
__license__ = 'THE LICENSE'
__status__ = 'development'
__docformat__ = 'reStructuredText'

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm, remove_perm


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError(_(u"Users must have an email address"))

        user = self.model(
            email=self.normalize_email(email),
            name=name)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User to manage Edoo tasks.

    User adds some utility fields, this extension could be seen as an
    user profile for ``contrib.auth.models.User`` and it's further extended
    in the profiles applicaiton. This object is intended to wrap the
    authentication User object with some bussiness data needed by Edoo.

    :members:
    """

    objects = UserManager()

    email = models.EmailField(
        verbose_name=_(u"Email"),
        unique=True,
        max_length=255)
    """ Use it as EmailField. """

    name = models.CharField(_(u"Nombre"), max_length=255)
    """ Use it as CharField. """

    is_active = models.BooleanField(default=True)
    """ Use it as BooleanField. """

    is_admin = models.BooleanField(default=False)
    """ Use it as BooleanField. """

    phone = models.CharField(_(u"Número de teléfono"), max_length=50, null=True)
    """ Use it as CharField. """

    # Configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return "%s <%s>" % (self.name, self.email)

    # https://docs.djangoproject.com/es/1.9/topics/auth/customizing/


class PasswordRetrievalEvent(models.Model):
    """
    When a user needs to retrieve it's lost password, we use this model to
    register the event. The token is generated to avoid malicious impersonation.

    :members:
    """

    user = models.ForeignKey(User, verbose_name=_(u"Usuario"))
    """ ForeignKey to ``users.models.User``. """

    token = models.CharField(_(u"Token"), max_length=20)
    """ Unique string identifier for the petition. Use it as CharField. """

    is_consumed = models.BooleanField(_(u"¿Está consumido?"), default=False)
    """
    Flag indicating if the request has been consumed. Use it as BooleanField.
    """
