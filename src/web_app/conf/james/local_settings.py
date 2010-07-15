#Copyright 2010 James Saunders
#
#This file is part of Web BPDA.
#
#Web BPDA is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Web BPDA.  If not, see <http://www.gnu.org/licenses/>.
def local_start(context):
    """Configuration to run at the beginning, settings made here can
    be over-ridden but it useful for setting up path variables used
    elsewhere in the config."""

def local_end(context):
    """Configuration to run at the end. Can override all other
    configs, and is where you would put settings to have the final say
    in configuration."""

    context['DATABASE_ENGINE'] = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    context['DATABASE_NAME'] = 'temp.db'             # Or path to database file if using sqlite3.
    context['DATABASE_USER'] = ''             # Not used with sqlite3.
    context['DATABASE_PASSWORD'] = ''         # Not used with sqlite3.
    context['DATABASE_HOST'] = ''             # Set to empty string for localhost. Not used with sqlite3.
    context['DATABASE_PORT'] = ''             # Set to empty string for default. Not used with sqlite3.
    
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

