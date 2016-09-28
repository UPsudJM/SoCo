import datetime
from flask_babel import gettext, format_date
from flcoll import app

@app.template_filter('datefr')
def datefr_filter(d, fmt=None):
    if fmt:
        return format_date(d, fmt)
    return format_date(d, "medium")
