from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *

from datetime import datetime
import time

from viz import viz_page
from utils import has_no_empty_params

###############################################
#      Define navbar with logo                #
###############################################
#here we define our menu items
topbar = Navbar(View('Home', 'home'),
                # View('Search', 'viz.search'),
                View('Deepdive', 'viz.deepdive'),
                View('Temperature', 'viz.temperature'),
                View('Disasters', 'viz.disasters'),
                View('Team', 'team'),
                )

# registers the "top" menubar
nav = Nav()
nav.register_element('top', topbar)

app = Flask(__name__)
app.register_blueprint(viz_page)
Bootstrap(app)

###############################################
#                Routes                       #
###############################################

@app.route("/")
def home():
    return render_template("index.html",
                            title="Home")

@app.route('/team')
def team():
    return render_template('team.html', title='Team',
                            charlie_png=url_for('static', filename='charlie.png'),
                            jash_png=url_for('static', filename='jash.png'),
                            justin_png=url_for('static', filename='justin.png'),
                            stephen_png=url_for('static', filename='stephen.png'),
                            )

@app.route("/site-map")
def site_map():
    '''
    Returns all routes
    '''
    get_links = []
    post_links = []
    all_endpoints = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            get_links.append((url, rule.endpoint))
        if "POST" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            post_links.append((url, rule.endpoint))
        all_endpoints.append(rule.endpoint)
    # links is now a list of url, endpoint tuples

    return render_template('site-map.html', get_links=get_links,
                           post_links=post_links,
                           all_endpoints=all_endpoints,
                           status='ALIVE',
                           time=datetime.fromtimestamp(time.time()))

nav.init_app(app)

if __name__ == "__main__":
    app.run()
