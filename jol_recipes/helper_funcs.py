import json

def get_recipe_data(submitted_name,recipes):

    for recipe in recipes:
        if recipe['safe_name'] == submitted_name:
            with open('data/recipes/' + submitted_name + '.json') as f1:
                recipe_data = json.load(f1)
                return recipe_data
    
    return False
    