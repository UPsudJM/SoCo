import datetime
from flask_babel import gettext, format_date
from PIL import Image
from config import LOGO_FOLDER, LOGO_URL_REL
from flcoll import app


@app.template_filter('datefr')
def datefr_filter(d, fmt=None):
    if fmt:
        return format_date(d, fmt)
    return format_date(d, "medium")

@app.template_filter('ouinon')
def ouinon_filter(b, non="non"):
    if b==True:
        return "oui"
    else:
        return non

@app.template_filter('afflogo')
def afflogo_filter(f, size=(64,64)):
    infile = LOGO_FOLDER + f
    thumbnail = "petit-" + f
    outfile = LOGO_FOLDER + thumbnail
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
        return LOGO_URL_REL + thumbnail
