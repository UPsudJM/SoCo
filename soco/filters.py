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
