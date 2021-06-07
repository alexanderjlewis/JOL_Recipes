import json

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