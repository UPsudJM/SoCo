Requirements
============
Debian packages
---------------
* `python3` `python3-pil` `python3-flask` `python3-pip`
* `python3-venv` if you wish to use python virtual environment (recommended)
* + you will need a web server

Database
--------
* postgresql postgresql-server-dev-x.y (you can uninstall it once psycopg2 is compiled)
* or MySQL
* or any database if you tweek the configuration a little

Python packages
---------------
* if you use virtualenv: `$ pyvenv venv` then `source venv/bin/activate`
* `$ pip3 install Flask-Admin Flask-Babel Flask-Login Flask-Mail Flask-RESTful Flask-WTF Pillow Flask-Babelex`
* `$ pip3 install SQLAlchemy sqlalchemy-migrate psycopg2 (or flask-mysqldb)`
* `$ pip3 install ldap3` (if you want to use LDAP for user identification) or `$ pip3 install passlib` (otherwise)
* `$ pip3 install scipy zbar-py Flask-QRCode` (only if you want ticketing)

LaTeX
-----
_required for printing documents and badges_
* Debian packages: `texlive-latex-base` `texlive-fonts-recommended`
* For French-speaking: `texlive-lang-french`
* you will want to have a look at .tex templates (in [./soco/templates])


Installation
============
Files
-----
* clone or download SoCo code into your working directory
* create a sub-directory for compiling LaTeX files
  * permissions: SoCo needs to write in it
  * paths: look at the paths in the LaTeX templates, esp [./soco/templates/etiquettes.tex] in order to make your static files accessible from the LaTeX files that will be compiled there
* if you wish, create another subdir for PDF files (you may use /tmp)
* feed the corresponding variables FABDIR and TMPDIR in [./config.py]
* create a `./logs` subdir, or configure LOG_FILE in [./config.py]

Javascript modules
------------------
SoCo's interactions are based on angular.js. Corresponding modules are packaged with the software.

Warning: If you are not in France, you might want to adapt the locale and maybe some of the code.

Database configuration
----------------------
_(shown here for PostGreSQL)_

```$ sudo su - postgres
$ createuser -e [-d] -P -s superuser
$ createdb -e -O superuser soco
$ createuser my_user
$ psql [-W]
> GRANT SELECT,UPDATE,INSERT,DELETE ON ALL TABLES IN SCHEMA public TO myuser;
> GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO myuser;
> ALTER USER my_user WITH PASSWORD 'mypass'```

_(or for MySQL/MariaDB)_

```mysql>  CREATE DATABASE soco DEFAULT CHARACTER SET 'utf8' COLLATE utf8_general_ci;
mysql> GRANT SELECT,UPDATE,INSERT,DELETE ON soco.* TO myuser IDENTIFIED BY 'mypass';```

Software configuration
----------------------
* Most of the config parameters are set in [./config.py]
* Yet for the most secret ones, you will want to create a file with name [./secret.py], like:

```PGSQL_DATABASE_USER = 'your_user'
PGSQL_DATABASE_PASSWORD = 'password_for_your_user'
SECRET_KEY = 'your long and very secret key'
ADMINS = ['email-admin1@your-organization.com', 'email-admin2@your-organization.com']```

* then uncomment corresponding lines in [./config.py]

Web server configuration
------------------------
Should you wish to run SoCo behind Apache2, then

WSGIDaemonProcess soco user=www-data group=www-data threads=5 home=/path_to/soco
WSGIScriptAlias / /path_to/soco/soco.wsgi

or, if you run SoCo inside a python virtual environment :

WSGIDaemonProcess soco user=www-data group=www-data threads=5 home=/var/www/soco python-path=/path_to_your_venv_site-packages:/path_to/soco
WSGIScriptAlias / /path_to/soco/soco.wsgi
