#app.py
import json
from gen import generate
from flask import Flask, render_template, url_for, send_file

app = Flask(__name__)
with open('data/recipe_list.json') as f:
    recipes = json.load(f)
with open('data/ingredient_list.json') as f:
    ingredients = json.load(f)

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/list')
def list_page():
    return render_template('list.html', recipes=recipes)


@app.route('/api/getList')
def getList():
    return "<p>Got it!</p>"

@app.route('/recipe/<name>')
def render_recipe_page(name=None):
    render_recipe = None
    for recipe in recipes:
        if recipe['safe_name'] == name:
            with open('data/recipes/' + name + '.json') as f1:
                recipe_data = json.load(f1)
    chart = generate(recipe_data, ingredients)
    return render_template('chart.html', recipe=recipe_data, chart=chart)

@app.route('/sw.js')
def sw():
    return send_file('static/js/sw.js')

@app.route('/offline')
def offline():
    return render_template('offline.html')