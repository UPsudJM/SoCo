from re import compile as rcompile
from os import chdir, remove
try:
    from subprocess import run, TimeoutExpired
except:
    from subprocess import call, TimeoutExpired
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

TPL_ETIQUETTE="\
\put(%d,%d){\crophrule \cropvrule}\
\put(%d,%d){\makebox(85,50){\card{%s}{%s}{%s}{%s}}}"

TPL_ETIQUETTE_VIDE="\
\put(%d,%d){\crophrule \cropvrule}\
\put(%d,%d){\makebox(85,50){\hspace{1cm}}}"

TPL_PAGE_ETIQUETTES="\
\\begin{picture}(210,270)(0,0)\
\color{light-gray}\
%s\
\put(271,320){\cropvrule \crophrule}\
\put(271,266){\cropvrule \crophrule}\
\put(271,212){\cropvrule \crophrule}\
\put(-10,156){\crophrule}\
\put(083,156){\crophrule}\
\put(173,156){\crophrule}\
\
\put(-03,149){\cropvrule}\
\put(090,149){\cropvrule}\
\put(180,149){\cropvrule}\
\put(270,149){\cropvrule}\
\
\put(090,156){\crophrule}\
\put(180,156){\crophrule}\
\put(270,156){\crophrule}\
\
\end{picture}\
"

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

def fabrique_page_etiquettes(etiquettes):
    l = len(etiquettes)
    try:
        assert l <= 9
    except AssertionError:
        flash("Erreur dans la fabrication des étiquettes")
        return render_template('500.html')
    return TPL_PAGE_ETIQUETTES % "".join(etiquettes)

texenv = app.create_jinja_environment()
texenv.block_start_string = '((*'
texenv.block_end_string = '*))'
texenv.variable_start_string = '((('
texenv.variable_end_string = ')))'
texenv.comment_start_string = '((='
texenv.comment_end_string = '=))'
texenv.filters['escape_tex'] = escape_tex
