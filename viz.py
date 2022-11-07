from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

viz_page = Blueprint('viz', __name__,
                    url_prefix='/viz',
                    template_folder="templates/viz")

@viz_page.route('/temperature')
def temperature():
    try:
        return render_template("temperature.html", title="Temperature")
    except TemplateNotFound:
        abort(404)

@viz_page.route('/disasters')
def disasters():
    try:
        return render_template("disasters.html", title="FEMDA Declared Disasters")
    except TemplateNotFound:
        abort(404)
