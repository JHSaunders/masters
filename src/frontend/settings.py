# Django settings 

import os
import logging

def settings_main(context):
    preinit(context)
    local_start(context)
    setup(context)
    local_end(context)

def preinit(context):
    """ Define variables which may well be over-ridden by local_start() """
    context['SPACE_HOME'] = os.environ['PWD']

    find_local_config(context)

def find_local_config(context):
    """ Load the local config file. This should define functions like
    local_start and local_end, all of which take a context
    dictionary. This function just makes those functions available, it
    doesn't execute them"""
    if os.environ.has_key("LOCAL_CONF_NAME"):
        conf_name = os.environ["LOCAL_CONF_NAME"]
#        print "Using conf " + conf_name
        local_settings_file = "conf/" + conf_name + "/local_settings.py"
        if not os.path.exists(local_settings_file):
            raise("Couldn't find config file " + local_settings_file)
        execfile(local_settings_file, context)
    else:
        pass
 #       print "No local config"

        # Create the local functions dynamically.
        def null_func(*kwargs):
            pass
        context['local_start'] = null_func
        context['local_end'] = null_func

def setup(context):
    """Main setup. All variables defined in this function can be
    over-ridden by local_end"""
    context["DEBUG"] = True
    context["LOGGING_OUTPUT_ENABLED"] = False
    context["LOGGING_LOG_SQL"] = False
    context["TEMPLATE_DEBUG"] = context["DEBUG"]

    context["ADMINS"] = (
        ('james', 'james.h.saunders@gmail.com'),
    )

    context["MANAGERS"] = context["ADMINS"]

    context["DATABASE_ENGINE"] = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    context["DATABASE_NAME"] = 'temp.db'             # Or path to database file if using sqlite3.
    context["DATABASE_USER"] = ''             # Not used with sqlite3.
    context["DATABASE_PASSWORD"] = ''         # Not used with sqlite3.
    context["DATABASE_HOST"] = ''             # Set to empty string for localhost. Not used with sqlite3.
    context["DATABASE_PORT"] = ''             # Set to empty string for default. Not used with sqlite3.

    # Local time zone for this installation. Choices can be found here:
    # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    # although not all choices may be available on all operating systems.
    # If running in a Windows environment this must be set to the same as your
    # system time zone.
    context["TIME_ZONE"] = 'Africa/Harare'

    # Language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    context["LANGUAGE_CODE"] = 'en-us'

    context["SITE_ID"] = 1

    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    context["USE_I18N"] = True

       # Absolute path to the directory that holds media.
    # Example: "/home/media/media.lawrence.com/"
    context["MEDIA_ROOT"] = context['SPACE_HOME']+"/media/"

    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash if there is a path component (optional in other cases).
    # Examples: "http://media.lawrence.com", "http://example.com/media/"
    context["MEDIA_URL"] = '/media/'

    # URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
    # trailing slash.
    # Examples: "http://foo.com/media/", "/media/".
    context["ADMIN_MEDIA_PREFIX"] = '/admin_media/'
    
    context["DEBUG"] = True
    
    # Make this unique, and don't share it with anybody.
    context["SECRET_KEY"] = '-3x)yts$szlmu@l7msjykg%tw4-8v9(n+ik=9=tt)i1iv2u(b$'

    # List of callables that know how to import templates from various sources.
    context["TEMPLATE_LOADERS"] = (
        'django.template.loaders.filesystem.load_template_source',
        'django.template.loaders.app_directories.load_template_source',
    #     'django.template.loaders.eggs.load_template_source',
    )

    context["MIDDLEWARE_CLASSES"] = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        #'django.middleware.cache.CacheMiddleware',
        'django.middleware.transaction.TransactionMiddleware',
        #'djangologging.middleware.LoggingMiddleware',
    )

    context["LOGIN_REDIRECT_URL"] = '/accounts/login/'
    context["LOGIN_URL"] = context["LOGIN_REDIRECT_URL"]

    # required for logging
    context["INTERNAL_IPS"] = (
        '127.0.0.1',
    )

    context["LOGGING_FILE"] = "ndibano.log"
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )

    context["ROOT_URLCONF"] = 'urls'

    context["TEMPLATE_DIRS"] = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
    )

    context["INSTALLED_APPS"] = (
        'web_bayes',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'django.contrib.admindocs',        
        'tabs'
    )
    
settings_main(globals())
