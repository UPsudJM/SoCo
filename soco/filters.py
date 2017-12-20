"""
§ This file is part of SoCo.                                            §
§                                                                       §
§ SoCo is free software: you can redistribute it and/or modify          §
§ it under the terms of the GNU General Public License as published by  §
§ the Free Software Foundation, either version 3 of the License, or     §
§ (at your option) any later version.                                   §
§                                                                       §
§ SoCo is distributed in the hope that it will be useful,               §
§ but WITHOUT ANY WARRANTY; without even the implied warranty of        §
§ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         §
§ GNU General Public License for more details.                          §
§                                                                       §
§ You should have received a copy of the GNU General Public License     §
§ along with SoCo.  If not, see <http://www.gnu.org/licenses/>.         §
§                                                                       §
§ © 2016-2017 Odile Bénassy, Université Paris Sud                       §
§                                                                       §
"""
# coding: utf-8

import datetime, string, random
from jinja2 import contextfilter
from flask_babel import format_date, format_datetime
from soco import app


@app.template_filter('localedate')
def localedate_filter(d, fmt=None):
    if fmt:
        return format_date(d, fmt)
    return format_date(d, "medium")

@app.template_filter('localedatetime')
def localedatetime_filter(d, fmt=None):
    if fmt:
        return format_datetime(d, fmt)
    return format_datetime(d, "dd/MM H:mm")

@app.template_filter('datedebutcompl')
def datedebutcompl_filter(d, date_fin, fmt=None):
    if (date_fin - d).days==1:
        return "les " + datedebut_filter(d, date_fin, fmt) + " et"
    return "du " + datedebut_filter(d, date_fin, fmt) + " au"

@app.template_filter('datedebut')
def datedebut_filter(d, date_fin, fmt=None):
    # Tester si même mois et année, ou si même année
    if d.year == date_fin.year and d.month == date_fin.month:
        return format_date(d, "d")
    elif d.year == date_fin.year:
        return format_date(d, "d MMMM")
    if fmt:
        return localedate_filter(d, fmt)
    return localedate_filter(d, "medium")

@app.template_filter('ouinon')
def ouinon_filter(b, non="non"):
    if b==True:
        return "oui"
    else:
        return non

@app.template_filter('generate_default_password')
@contextfilter
def generate_default_password_filter(context, s):
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.sample(char_set*7, 7))

@app.template_filter('tohtml')
def tohtml_filter(s):
    return s.replace("\n", "<br/><br/>")
