import json

def load_recipes():
    with open('data/recipe_list.json') as f:
        recipes = json.load(f)
    return recipes
    
def load_ingredients(): 
    with open('data/ingredient_list.json') as f:
        ingredients = json.load(f)
    return ingredients