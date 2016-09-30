from re import compile as rcompile
from os import chdir, remove
from subprocess import run, TimeoutExpired, CalledProcessError
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

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
        return newval

def genere_pdf(texcode, prefix="", timeout=10, check=True):
    chdir("./pdf")
    fd, texfilename = mkstemp(prefix=prefix, suffix=".tex", dir=".")
    try:
        open(texfilename, 'wb').write(texcode.encode("latin-1"))
    except:
        print("erreur d'écriture ou de recodage")
    try:
        r = run([PDFCMD, texfilename], timeout=timeout)
    except TimeoutExpired as err:
        chdir("..")
        return err
    except CalledProcessError as err:
        chdir("..")
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
