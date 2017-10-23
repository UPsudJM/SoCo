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

import datetime
from flask_babel import gettext, format_date, format_datetime
from PIL import Image
from soco import app


@app.template_filter('datefr')
def datefr_filter(d, fmt=None):
    if fmt:
        return format_date(d, fmt)
    return format_date(d, "medium")

@app.template_filter('datetimefr')
def datetimefr_filter(d, fmt=None):
    if fmt:
        return format_datetime(d, fmt)
    return format_datetime(d, "dd/MM H:mm")

@app.template_filter('datedebut')
def datedebut_filter(d, date_fin, fmt=None):
    # Tester si même mois et année, ou si même année
    if d.year == date_fin.year and d.month == date_fin.month:
        return datefr_filter(d, "d")
    elif d.year == date_fin.year:
        return datefr_filter(d, "d MMMM")
    if fmt:
        return datefr_filter(d, fmt)
    return datefr_filter(d, "medium")

@app.template_filter('ouinon')
def ouinon_filter(b, non="non"):
    if b==True:
        return "oui"
    else:
        return non

@app.template_filter('afflogo')
def afflogo_filter(f, size=(64,64)):
    infile = app.config['LOGO_FOLDER'] + f
    thumbnail = "petit-" + f
    outfile = app.config['LOGO_FOLDER'] + thumbnail
    try:
        im = Image.open(outfile)
    except IOError:
        try:
            im = Image.open(infile)
            im.thumbnail(size)
            im.save(outfile, "PNG")
        except IOError:
            print("cannot create thumbnail for", f)
    finally:
        return app.config['LOGO_URL_REL'] + thumbnail
