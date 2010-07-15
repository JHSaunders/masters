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
import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

os.environ['LOCAL_CONF_NAME'] = 'server'
os.environ['DJANGO_SETTINGS_MODULE'] = 'web_app.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

