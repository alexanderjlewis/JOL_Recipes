import json
import urllib.parse
import os

def load_recipes():
    with open('data/recipe_list.json') as f:
        recipes = json.load(f)
    return recipes
    
def load_ingredients(): 
    with open('data/ingredient_list.json') as f:
        ingredients = json.load(f)
    return ingredients
    
def get_recipe_data(submitted_name,recipes):

    for recipe in recipes:
        if recipe['safe_name'] == submitted_name:
            with open('data/recipes/' + submitted_name + '.json') as f1:
                recipe_data = json.load(f1)

                # process the json to assemble a unique list of ingredient categories - this is required for templates that expect this list
                ingredient_categories = []
                for ingredient in recipe_data['ingredients']:
                    if ingredient['category'] not in ingredient_categories:
                        ingredient_categories.append(ingredient['category'])
                recipe_data['ingredient_categories'] = ingredient_categories

                return recipe_data
    
    return False


def adjust_recipe_qty(recipe, multiplier):
    
    for step_id in recipe['steps']:
        for ingredient in recipe['steps'][str(step_id)]['ingredients']:
            try:
                ingredient['quantity'] = float(ingredient['quantity']) * multiplier
                ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
            except:
                pass

    for ingredient in recipe['ingredients']:
        try:
            ingredient['quantity'] = float(ingredient['quantity']) * multiplier
            ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
        except:
            pass
    
    return recipe


def unit_conversion(submitted_ingredient):

    with open('data/conversions.json') as f1:
        conversion_data = json.load(f1)

    output = {}
    output['input'] = submitted_ingredient

    input_qty, input_unit = submitted_ingredient.split(' ')
    input_qty = float(input_qty)
    output['conversions'] = []

    if conversion_data.get(input_unit):
        for item in conversion_data[input_unit]:
            output_qty = float(input_qty) * item['factor']
            output_qty = str(round(output_qty, 3)).rstrip('0').rstrip('.')
            output['conversions'].append({'qty':output_qty,'unit':item['to_unit']})
    else:
        output['conversions'].append({'qty':'No Conversion Available for this Unit','unit':''})
        
    return output

def url_safe_string(string_data):
    '''
    Transformhelp() a string in a url safe form

            Parameters:
                    string_data (str): A string to tranform

            Returns:
                    string_data (str): A url safe version of the supplied string
    '''
    
    #proceess the name into a url safe format with '_' instead of space chars
    string_data = string_data.replace(' ', '_').lower()
    string_data = urllib.parse.quote(string_data, safe='')

    return string_data

def create_new_recipe(form_data, recipes):

    response_success = True
    response_data = {}
    new_recipe = {}

    new_recipe['name'] = form_data['inputRecipeName']
    
    new_recipe['safe_name'] = url_safe_string(new_recipe['safe_name'])

    new_recipe['tag_line'] = form_data['inputTagLine']
    new_recipe['tags_info'] = []
    new_recipe['tags_green'] = []
    new_recipe['publish'] = True

    for recipe in recipes:
        if new_recipe['name'].lower() == recipe['name'].lower():
            response_success = False
            response_data['submitted_name'] = 'This recipe name is already in use.'

    if form_data['vegeQn'] == 'Yes':
        new_recipe['tags_green'].append('Vege')
    
    if form_data['inputInfoTag1']:
        new_recipe['tags_info'].append(form_data['inputInfoTag1'])
    
    if form_data['inputInfoTag2']:
        new_recipe['tags_info'].append(form_data['inputInfoTag2'])

    if form_data['inputInfoTag3']:
        new_recipe['tags_info'].append(form_data['inputInfoTag3'])

    if response_success:
        with open('data/recipe_list.json', "r") as f:
            recipes = json.load(f)

        recipes.append(new_recipe)

        with open('data/recipe_list.json', "w") as f:
            json.dump(recipes, f)

        with open('data/recipe_template.json', "r") as f:
            recipe_template = json.load(f)

        recipe_template['name'] = new_recipe['name']
        recipe_template['safe_name'] = new_recipe['safe_name']

        with open('data/recipes/' + new_recipe['safe_name'] + '.json', "w") as f:
            json.dump(recipe_template, f)

        response_data['safe_name'] = new_recipe['safe_name']

    
    return response_success, response_data

def delete_recipe(recipe_to_delete):
    
    with open('data/recipe_list.json', "r") as f:
        recipes = json.load(f)

    for recipe in recipes:
        if recipe['safe_name'] == recipe_to_delete:
            temp = recipe

    if temp:
        recipes.remove(temp)

    with open('data/recipe_list.json', "w") as f:
        json.dump(recipes, f)

    path_to_recipe = 'data/recipes/' + recipe_to_delete + '.json'
    if os.path.exists(path_to_recipe):
        os.remove(path_to_recipe)

    pass

def add_ingredient(data):
    
    response = {"status":'',"data":{}}

    try:
        new_ingredient = {}
        new_ingredient['name'] = data['name']
        new_ingredient['category'] = data['category']
        new_ingredient['qty'] = data['qty']
        new_ingredient['unit'] = data['unit']
        
        file_path = 'data/recipes/' + data['recipe_safe_name'] + '.json'
        with open(file_path, "r") as f: # the recipe name should exist as a file.
            recipe = json.load(f)

        recipe['ingredients'].append(new_ingredient)

        with open(file_path, "w") as f:
            json.dump(recipe, f)

    except:
        response['status'] = 'general_error'
        response['status']['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.003</span>'

    return response

def edit_ingredient(data):
    response = {"status":'success',"data":{}}
    
    return response