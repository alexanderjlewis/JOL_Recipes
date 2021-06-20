import json
import urllib.parse
import os

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


def create_new_recipe(form_data, recipes):
    
    print(form_data)

    response_success = True
    response_data = {}
    new_recipe = {}

    new_recipe['name'] = form_data['inputRecipeName']
    
    #proceess the name into a url safe format with '_' instead of space chars
    new_recipe['safe_name'] = new_recipe['name'].replace(' ', '_').lower()
    new_recipe['safe_name'] = urllib.parse.quote(new_recipe['safe_name'], safe='')

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

def add_ingredient(form_data):
    
    response = {"status":"success","data":{}}

    while True:
        #Check 1: Confirm the submitted recipe name exists (hidden field on the front end form)
        try: #try parse the submitted name and open the file
            submitted_recipe_safe_name = str(form_data['inputRecipeSafeName'])
            file_path = 'data/recipes/' + submitted_recipe_safe_name + '.json'
            with open(file_path, "r") as f:
                recipe = json.load(f)  
        except: #if that fails we need to throw a generic error response. It probably means someone is manipulating requests rather then using the UI.
            response['status'] = 'general_error'
            response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.001</span>'
            break

        #Check 2: Confirm if the ingredient name already exists
        try:
            submitted_ingredient_name = str(form_data['inputIngredientName'])
            if submitted_ingredient_name:
                ingredient_found = False
                for ingredient in recipe['ingredients']:
                    if ingredient['name'].lower() == submitted_ingredient_name.lower():
                        ingredient_found = True
            else:
                response['status'] = 'error'
                response['data']['inputIngredientName'] = 'This field is mandatory - please enter an ingredient category.'
        except:
            response['status'] = 'general_error'
            response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.002</span>'
            break

        #Check 3: Check that the mode value is allowable makes sense in context with the supplied ingredient name 
        try:
            mode = str(form_data['inputMode'])
            if mode != 'edit' and mode != 'add': # only 'edit' and 'add' are valid mode values 
                raise ValueError('Unexpected value in form mode attribute')
        except:
            response['status'] = 'general_error'
            response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.003</span>'
            break

        #Check 4: Check that mode/ingredient name make sense with each other in context
        try:
            if mode == 'edit':    
                if not ingredient_found: # in edit mode, the ingredient name is expected to be found
                    raise ValueError('Unexpected value in form mode attribute')
            elif mode == 'add':
                print('a')
                if ingredient_found: # in add mode, the ingredient name supplied shouldn't exist. If it does we return an error to UI.
                    response['status'] = 'error'
                    response['data']['inputIngredientName'] = 'This ingredient name already exists. Please enter a different name.' 
        except:
            response['status'] = 'general_error'
            response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.004</span>'
            break

        #Check 5: Check that the category can be cast to a string and is not null.
        try:
            submitted_ingredient_category = str(form_data['inputIngredientCategory'])
            if not submitted_ingredient_category:
                response['status'] = 'error'
                response['data']['inputIngredientCategory'] = 'This field is mandatory - please enter an ingredient category.' 
        except:
            response['status'] = 'error'
            response['data']['inputIngredientCategory'] = 'The provided value is not a valid input.' 
            break

        #Check 6: Check that the qty can be cast to a floatl
        try:
            if form_data['inputIngredientQty']:
                submitted_ingredient_qty = float(form_data['inputIngredientQty'])
        except:
            response['status'] = 'error'
            response['data']['inputIngredientQty'] = 'The provided value is not a valid number.' 
            break

        #Check 7: Check that the unit can be cast to a string
        try:
            submitted_ingredient_unit = str(form_data['inputIngredientUnit'])
        except:
            response['status'] = 'error'
            response['data']['inputIngredientUnit'] = 'The provided value is not a valid input.' 
            break

        break

    return response