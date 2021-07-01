import json

def validate_add_edit_ingredient_data(form_data):
    
    validation_passed = True
    validation_status = ''
    validation_response = {}
    submitted_data = {}

    while True:
        #Check 1: Confirm that all submitted values can be parsed into their expected data type
        try:
            submitted_data['recipe_safe_name'] = str(form_data['inputRecipeSafeName'])
            file_path = 'data/recipes/' + submitted_data['recipe_safe_name'] + '.json'
            with open(file_path, "r") as f: # the recipe name should exist as a file.
                recipe = json.load(f)  
            
            submitted_data['mode'] = str(form_data['inputMode'])
            if submitted_data['mode'] != 'add' and submitted_data['mode'] != 'edit': #add and edit are the only allowed modes
                raise ValueError('Unexpected value in form the form "mode" attribute')
            
            submitted_data['name'] = str(form_data['inputIngredientName'])
            submitted_data['category'] = str(form_data['inputIngredientCategory'])
            if form_data['inputIngredientQty']:
                submitted_data['qty'] = float(form_data['inputIngredientQty'])
            else:
                submitted_data['qty'] = ''
            submitted_data['unit'] = str(form_data['inputIngredientUnit'])

        except: #if this fails it probably means someone is manipulating requests rather then using the UI.
            validation_status = 'general_error'
            validation_response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.001</span>'
            break
    
        #Check 3: Make sure ingredient name submitted makes sense in context of mode
        try:
            if not submitted_data['category']:
                validation_status = 'field_error'
                validation_response['inputIngredientCategory'] = 'This field is mandatory - please enter an ingredient category.'

            if not submitted_data['name']:
                validation_status = 'field_error'
                validation_response['inputIngredientName'] = 'This field is mandatory - please enter an ingredient name.'
            else:
                ingredient_found = False
                for ingredient in recipe['ingredients']:
                    if ingredient['name'].lower() == submitted_data['name'].lower():
                        ingredient_found = True
                if submitted_data['mode'] == 'edit':    
                    if not ingredient_found: # in edit mode, the ingredient name is expected to be found
                        raise ValueError('Unexpected value in form mode attribute')
                elif submitted_data['mode'] == 'add':
                    if ingredient_found: # in add mode, the ingredient name supplied shouldn't exist. If it does we return an error to UI.
                        validation_status = 'field_error'
                        validation_response['inputIngredientName'] = 'This ingredient name already exists. Please enter a different name.' 
        except:
            validation_status = 'general_error'
            validation_response['error_msg'] = '<strong>An unexpected error occured.</strong><br>Please reload the page and/or try agin later.<span style="float:right;">ERR#1.002</span>'
            break

        break

    if validation_status: 
        validation_passed = False

    return validation_passed, validation_status, validation_response, submitted_data