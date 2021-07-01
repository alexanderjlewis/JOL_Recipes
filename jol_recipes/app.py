#app.py
import json
from gen import generate
from flask import Flask, render_template, url_for, send_file, request, jsonify, redirect
import helper_funcs
from validation import validate_add_edit_ingredient_data

app = Flask(__name__)

recipes = helper_funcs.load_recipes()
ingredients = helper_funcs.load_ingredients()

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
    recipe_data = helper_funcs.get_recipe_data(submitted_name, recipes)
    recipe_data = helper_funcs.adjust_recipe_qty(recipe_data, multiplier)
    chart = generate(recipe_data)
    return chart

@app.route('/api/getIngredientConversion')
def api_getIngredientConversion():
    submitted_ingredient = request.args.get('input')
    processed_data = helper_funcs.unit_conversion(submitted_ingredient)
    return render_template('conversion_modal.html', data=processed_data, mode='edit')

@app.route('/api/createRecipe', methods=['POST'])
def api_createRecipe():
    global recipes

    success, response_data = helper_funcs.create_new_recipe(request.form, recipes)
    
    recipes = helper_funcs.load_recipes()
    
    #if the processing doesn't return a response, we know if was sucessful and therefore redirect the user to the new page.
    if success:
        response_data['redirect'] = '/recipe/' + response_data['safe_name'] + '/edit'
    return (json.dumps(response_data), 200)

@app.route('/api/deleteRecipe', methods=['DELETE'])
def api_deleteRecipe():
    global recipes

    data = request.get_json()
    success = helper_funcs.delete_recipe(data['recipe_to_delete'])

    #refresh the cached json data
    recipes = helper_funcs.load_recipes()

    return (jsonify('success'), 200)

@app.route('/api/<string:recipe_safe_name>/ingredient_list', methods=['GET'])
def api_getIngredientList(recipe_safe_name):
    multiplier = float(request.args.get('multiplier'))
    recipe_data = helper_funcs.get_recipe_data(recipe_safe_name, recipes)
    recipe_data = helper_funcs.adjust_recipe_qty(recipe_data, multiplier)
    return render_template('ingredient_list.html', recipe=recipe_data, mode='edit')

@app.route('/api/<string:recipe_safe_name>/ingredient_list', methods=['POST'])
def api_addIngredient(recipe_safe_name):
    validation_passed, validation_status, validation_response, submitted_data= validate_add_edit_ingredient_data(request.form)
    if validation_passed:
        if submitted_data['mode'] == 'add':
            response = helper_funcs.add_ingredient(submitted_data)
        else:
            response = helper_funcs.edit_ingredient(submitted_data)
    else:
        response = {'status':validation_status, 'data':validation_response}
    return (jsonify(response), 200)

@app.route('/api/<string:recipe_safe_name>/ingredient_list/<int:ingredient_id>', methods=['PUT'])
def api_updateIngredient(recipe_safe_name, ingredient_id):
    return (jsonify('ok'), 200)

@app.route('/api/<string:recipe_safe_name>/ingredient_list/<int:ingredient_id>', methods=['DELETE'])
def api_deleteIngredient(recipe_safe_name, ingredient_id):
    return (jsonify('ok'), 200)


@app.route('/recipe/<name>')
def render_recipe_page(name=None):
    recipe_data = helper_funcs.get_recipe_data(name, recipes)
    chart = generate(recipe_data)
    return render_template('chart.html', recipe=recipe_data, chart=chart)

@app.route('/recipe/<safe_name>/edit')
def render_recipe_edit_page(safe_name=None):
    recipe_data = helper_funcs.get_recipe_data(safe_name, recipes)
    chart = generate(recipe_data)
    return render_template('chart.html', recipe=recipe_data, chart=chart, mode='edit')

@app.route('/sw.js')
def sw():
    return send_file('static/js/sw.js')

@app.route('/offline')
def offline():
    return render_template('offline.html')
