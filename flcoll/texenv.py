from re import compile as rcompile
from os import chdir, remove
from subprocess import run, TimeoutExpired
from tempfile import mkstemp
from flcoll import app

PDFCMD = "/usr/bin/pdflatex"

LATEX_SUBS = (
    (rcompile(r'\\'), r'\\textbackslash'),
    (rcompile(r'([{}_#%&$])'), r'\\\1'),
    (rcompile(r'~'), r'\~{}'),
    (rcompile(r'\^'), r'\^{}'),
    (rcompile(r'"'), r"''"),
    (rcompile(r'\.\.\.+'), r'\\ldots'),
    )

TPL_ETIQUETTE="\put(-10,320){\crophrule \cropvrule}\
\put(000,270){\makebox(85,50){\card{%s}{%s}{%s}{%s}}}\
\put(083,320){\crophrule \cropvrule}"

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
        return newval

def genere_pdf(texcode, prefix="", timeout=10, check=True):
    chdir("./pdf")
    fd, texfilename = mkstemp(prefix=prefix, suffix=".tex", dir=".")
    try:
        t = texcode.encode("latin-1")
    except ValueError as err:
        print("erreur d'encodage : ", err.__doc__)
        chdir("..")
        return err
    try:
        open(texfilename, 'wb').write(t)
    except OSError as err:
        print("erreur d'écriture : ", err.__doc__)
        chdir("..")
        return err
    try:
        r = run([PDFCMD, texfilename], timeout=timeout)
    except TimeoutExpired as err:
        chdir("..")
        print("Timeout sur processus LaTeX %s" % texfilename, err.__doc__)
        return err
    except err:
        chdir("..")
        print("Erreur sur processus LaTeX %s" % texfilename, err.__doc__)
        return err
    pdffilename = texfilename[:-4] + ".pdf"
    remove(texfilename)
    remove(texfilename[:-4] + ".log") # fichier log généré par pdflatex
    remove(texfilename[:-4] + ".aux") # fichier aux généré par pdflatex
    chdir("..")
    return pdffilename


texenv = app.create_jinja_environment()
texenv.block_start_string = '((*'
texenv.block_end_string = '*))'
texenv.variable_start_string = '((('
texenv.variable_end_string = ')))'
texenv.comment_start_string = '((='
texenv.comment_end_string = '=))'
texenv.filters['escape_tex'] = escape_tex
