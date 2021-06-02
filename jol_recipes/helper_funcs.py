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