#app.py
import json
from gen import generate
from flask import Flask, render_template, url_for, send_file, request, jsonify, redirect
import config
from helper_funcs import get_recipe_data, adjust_recipe_qty, unit_conversion, create_new_recipe, delete_recipe, add_ingredient

app = Flask(__name__)
recipes = config.load_recipes()
ingredients = config.load_ingredients()

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/list')
def list_page():
    return render_template('list.html', recipes=recipes, mode='view')

@app.route('/list/edit')
def list_edit_page():
    return render_template('list.html', recipes=recipes, mode='edit')

@app.route('/api/getChart')
def api_getChart():
    submitted_name = request.args.get('recipe')
    multiplier = float(request.args.get('multiplier'))
    recipe_data = get_recipe_data(submitted_name, recipes)
    recipe_data = adjust_recipe_qty(recipe_data, multiplier)
    chart = generate(recipe_data)
    return chart

@app.route('/api/getIngredientList')
def api_getIngredientList():
    submitted_name = request.args.get('recipe')
    multiplier = float(request.args.get('multiplier'))
    recipe_data = get_recipe_data(submitted_name, recipes)
    recipe_data = adjust_recipe_qty(recipe_data, multiplier)
    return render_template('ingredient_list.html', recipe=recipe_data, mode='edit')

@app.route('/api/getIngredientConversion')
def api_getIngredientConversion():
    submitted_ingredient = request.args.get('input')
    processed_data = unit_conversion(submitted_ingredient)
    return render_template('conversion_modal.html', data=processed_data, mode='edit')

@app.route('/api/createRecipe', methods=['POST'])
def api_createRecipe():
    global recipes

    success, response_data = create_new_recipe(request.form, recipes)
    
    recipes = config.load_recipes()
    
    #if the processing doesn't return a response, we know if was sucessful and therefore redirect the user to the new page.
    if success:
        response_data['redirect'] = '/recipe/' + response_data['safe_name'] + '/edit'
    return (json.dumps(response_data), 200)

@app.route('/api/deleteRecipe', methods=['DELETE'])
def api_deleteRecipe():
    global recipes

    data = request.get_json()
    success = delete_recipe(data['recipe_to_delete'])

    #refresh the cached json data
    recipes = config.load_recipes()

    return (jsonify('success'), 200)

@app.route('/api/addEditIngredient', methods=['POST'])
def api_addIngredient():
    response = add_ingredient(request.form)
    return (jsonify(response), 200)

@app.route('/api/addIngredientCategory', methods=['POST'])
def api_addIngredientCategory():
    return (jsonify('success'), 200)

@app.route('/recipe/<name>')
def render_recipe_page(name=None):
    recipe_data = get_recipe_data(name, recipes)
    chart = generate(recipe_data)
    return render_template('chart.html', recipe=recipe_data, chart=chart)

@app.route('/recipe/<name>/edit')
def render_recipe_edit_page(name=None):
    recipe_data = get_recipe_data(name, recipes)
    chart = generate(recipe_data)
    return render_template('chart.html', recipe=recipe_data, chart=chart, mode='edit')

@app.route('/sw.js')
def sw():
    return send_file('static/js/sw.js')

@app.route('/offline')
def offline():
    return render_template('offline.html')
