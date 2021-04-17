import json

def get_recipe_data(submitted_name,recipes):

    for recipe in recipes:
        if recipe['safe_name'] == submitted_name:
            with open('data/recipes/' + submitted_name + '.json') as f1:
                recipe_data = json.load(f1)
                return recipe_data
    
    return False


def adjust_recipe_qty(recipe, quantity_required):
    
    multiplier = float(quantity_required) / float(recipe['serving_qty'])

    for step_id in recipe['steps']:
        for ingredient in recipe['steps'][str(step_id)]['ingredients']:
            try:
                ingredient['quantity'] = float(ingredient['quantity']) * multiplier
                ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
            except:
                pass

    for ingredient in recipe['ingredients_pantry']:
        try:
            ingredient['quantity'] = float(ingredient['quantity']) * multiplier
            ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
        except:
            pass

    for ingredient in recipe['ingredients_meat_veg']:
        try:
            ingredient['quantity'] = float(ingredient['quantity']) * multiplier
            ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
        except:
            pass

    for ingredient in recipe['ingredients_herbs_spices']:
        try:
            ingredient['quantity'] = float(ingredient['quantity']) * multiplier
            ingredient['quantity'] = str(round(ingredient['quantity'], 2)).rstrip('0').rstrip('.')
        except:
            pass
    
    return recipe