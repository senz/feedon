from flask import Blueprint, render_template, g, redirect

bp = Blueprint('landing_pages', __name__)

@bp.route('/')
def landing_page():
    if g.current_user:
        return redirect('/timelines/')

    return render_template("landing_pages/index.html")
