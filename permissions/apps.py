# -*- coding: utf-8 -*-

from django.apps import AppConfig

from django.db.models.signals import post_migrate
from django.conf import settings
from django.db import transaction


def add_default_permissions(sender, **kwargs):
    """
    This post migrate hook takes care of adding a custom permission too all our
    content types.
    """

    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission

    if hasattr(settings, 'DEFAULT_CUSTOM_PERMISSIONS'):

        with transaction.atomic():

            # For each of our content types
            for content_type in ContentType.objects.all():

                # For each permission in settings default custom permissions
                for perm in settings.DEFAULT_CUSTOM_PERMISSIONS:

                    # Build our permission slug
                    codename = '%(permission)s_%(content_type)s' % {
                        'permission': perm,
                        'content_type': content_type.model
                    }

                    # if it doesn't exist..
                    if not Permission.objects.filter(
                            content_type=content_type,
                            codename=codename):

                        # add it
                        Permission.objects.create(
                            content_type=content_type,
                            codename=codename,
                            name="Can %(permission)s %(content_type)s" % {
                                'permission': perm,
                                'content_type': content_type.name
                            }
                        )

                        print "Added %(permission)s permission for %(content_type)s" % {
                            'permission': perm,
                            'content_type': content_type.name
                        }


class PermissionsConfig(AppConfig):
    name = 'permissions'

    def ready(self):

        # Check for all our custom permissions after a migrate
        post_migrate.connect(add_default_permissions)
