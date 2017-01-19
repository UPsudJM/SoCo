import ldap3 as ldap
from flask import request, render_template, flash, redirect, url_for, Blueprint, g#, abort
from flask_login import current_user, login_user, logout_user, login_required
from flcoll import lm, db_session
from flcoll.auth.models import User, LoginForm

auth = Blueprint('auth', __name__)


@lm.user_loader
def load_user(user_id):
    if user_id:
        user = User.query.get(int(user_id))
        if user:
            user.authenticate()
            return user
    return None

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/')
@auth.route('/home')
def home():
    return render_template('home.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None \
        and current_user.is_authenticated:
        flash('Vous êtes déjà identifié-e.')
        return redirect(url_for('suivi'))

    form = LoginForm(request.form) #, nexturl=request.args['next'])
    if request.args and request.args.get('next'):
        form.nexturl.data = request.args['next']

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            auth_ok = User.try_login(username, password)
        except:
            raise
        if not auth_ok:
            flash('Login ou mot de passe invalide. Veuillez ré-essayer', 'danger')
            return render_template('login.html', form=form)

        user = User.query.filter_by(username=username).first()
        print(user)

        if not user:
            user = User(username)
            db_session.add(user)
            db_session.commit()
        user.authenticate()
        login_user(user, remember=True)
        flash('Identification réussie.', 'success')
        nexturl = request.form.get('nexturl')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        # FIXME
        #if not next_is_valid(nexturl):
        #    return flask.abort(400)
        return redirect(nexturl or url_for('suivi_index'))
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
