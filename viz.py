from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from viz_utils import *

viz_page = Blueprint('viz', __name__,
                    url_prefix='/viz',
                    template_folder="templates/viz")

@viz_page.before_request
def before_request():
    args = request.args
    width = args.get('width')
    height = args.get('height')
    if not width or not height:
        return """
        <script>
        (() => window.location.href = window.location.href + '?'+
        'width=' + window.innerWidth + '&height=' + window.innerHeight)()
        </script>
        """

@viz_page.route('/temperature')
def temperature():
    try:
        return render_template("/temperature.html", title="Temperature")
    except TemplateNotFound:
        abort(404)

@viz_page.route('/disasters')
def disasters():
    try:
        return render_template("/disasters.html", title="FEMA Declared Disasters")
    except TemplateNotFound:
        abort(404)

@viz_page.route('/search', methods=['GET', 'POST'])
def search():
    try:
        args = request.args
        width, height = determine_chart_dimensions(args)
        if request.method == 'GET':
            return render_template("/search.html", title="Search")
        if request.method == 'POST':
            name = request.form['text']
            json_chart = make_search_chart(raw_data=DATASET,
                                            width=width,
                                            height=height,
                                            incident=name.lower(),
                                            json=True)
            return render_template("/search.html",
                            title="Search",
                            input=name,
                            chart_json=json_chart
                            )
    except Exception as e:
        return "Something went wrong: " + e + e.message

@viz_page.route('/deepdive', methods=['GET', 'POST'])
def deepdive():
    try:
        args = request.args
        width, height = determine_chart_dimensions(args)
        domain = [args.get('begin_date','1979-01-01'), args.get('end_date','2022-11-01')]
        disaster_types = get_unique_disaster_types()
        if request.method == 'GET':
            json_chart = make_deepdive_chart(domain=domain,
                                            width=width,
                                            height=height,
                                            disaster_type='All',
                                            json=True
                                            )
            return render_template("/deepdive.html",
                                    title="Deepdive",
                                    disaster_types=disaster_types,
                                    chart_json=json_chart)
        if request.method == 'POST':
            disaster_type = request.form['disaster_type']
            json_chart = make_deepdive_chart(domain=domain,
                                            width=width,
                                            height=height,
                                            disaster_type=disaster_type,
                                            json=True
                                            )
            return render_template('/deepdive.html',
                                    title='Deepdive',
                                    disaster_type=disaster_type,
                                    disaster_types=disaster_types,
                                    chart_json=json_chart)
    except Exception as e:
        return "Something went wrong: " + e + e.message
