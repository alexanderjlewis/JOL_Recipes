#app.py
import json
from gen import generate
from flask import Flask, render_template, url_for, send_file, request, jsonify
import config
from helper_funcs import get_recipe_data

app = Flask(__name__)
recipes = config.load_recipes()
ingredients = config.load_ingredients()

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/list')
def list_page():
    return render_template('list.html', recipes=recipes)

@app.route('/api/getChart')
def api_getChart():
    submitted_name = request.args.get('recipe')
    quantity = int(request.args.get('quantity'))
    recipe_data = get_recipe_data(submitted_name, recipes)
    chart = generate(recipe_data, quantity)
    return jsonify(chart)

@app.route('/api/getIngredientList')
def api_getIngredientList():
    submitted_name = request.args.get('recipe')
    quantity = int(request.args.get('quantity'))
    recipe_data = get_recipe_data(submitted_name, recipes)
    return render_template('ingredient_list.html', recipe=recipe_data)

@app.route('/recipe/<name>')
def render_recipe_page(name=None):
    recipe_data = get_recipe_data(name, recipes)
    chart = generate(recipe_data)
    return render_template('chart.html', recipe=recipe_data, chart=chart)

@app.route('/sw.js')
def sw():
    return send_file('static/js/sw.js')

@app.route('/offline')
def offline():
    return render_template('offline.html')
