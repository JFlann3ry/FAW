from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

import mysql.connector

from datetime import datetime, timedelta

import base64



# Connect to MySQL
connection = mysql.connector.connect(
    host="192.168.68.114",
    user="jordan",
    password="jordan",
    database="Food"
)

views = Blueprint('views', __name__)

## views


# Define a function to calculate the week number based on your definition of a week
def get_week_number(date):
    start_of_week = date - timedelta(days=date.weekday())
    return start_of_week.isocalendar()[1]

@views.route('/')
def home():
    return render_template("index.html")
  
@views.route('/add-recipe', methods=['GET', 'POST'])
def addRecipe():
    if request.method == 'POST':
        data = request.get_json()
        tag_name = data.get('tag_name')

        if tag_name:
            # Insert the new tag into the database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Tags (TagName) VALUES (%s)", (tag_name,))
            connection.commit()

            # Fetch the ID of the newly inserted tag
            cursor.execute("SELECT LAST_INSERT_ID()")
            new_tag_id = cursor.fetchone()[0]

            cursor.close()

            # Return the ID of the newly inserted tag
            return jsonify({'tag_id': new_tag_id}), 200
        else:
            return jsonify({'error': 'Tag name not provided'}), 400
    else:
        # Fetch tags from the database
        cursor = connection.cursor()
        cursor.execute("SELECT id, tagName FROM Tags ORDER BY TagName")  # Assuming your column names are 'id' and 'tagName'
        tag_names = cursor.fetchall()
        cursor.close()
        # Render the template with tag_names included in the context
        return render_template("add-recipe.html", tag_names=tag_names)




@views.route('/save-recipe', methods=['POST'])
def save_recipe():
    # Extract data from the form
    recipe_name = request.form.get('recipe_name')
    description = request.form.get('description')
    url = request.form.get('url')
    oven_temp = request.form.get('oven_temp')
    time = request.form.get('time')
    tags = request.form.getlist('tags')
    photo = request.files['photo']
    ingredients_name = request.form.getlist('ingredient_name[]')
    instructions = request.form.getlist('instruction[]')
    quantities = request.form.getlist('quantity[]')
    units = request.form.getlist('unit[]')
    categories = request.form.getlist('category[]')
    steps = request.form.getlist('step[]')

    cursor = connection.cursor()

    # Insert into Recipe table
    cursor.execute("INSERT INTO Recipe (RecipeName, Description, URL, OvenTemp, Time) VALUES (%s, %s, %s, %s, %s)",
                   (recipe_name, description, url, oven_temp, time))
    recipe_id = cursor.lastrowid

    # Insert into xRecipeTags table
    for tag_id in tags:
        cursor.execute("INSERT INTO xRecipeTags (RecipeID, TagID) VALUES (%s, %s)", (recipe_id, tag_id))

    # Insert photo into Photos table
    photo_data = photo.read()
    cursor.execute("INSERT INTO Photos (Photo) VALUES (%s)", (photo_data,))
    photo_id = cursor.lastrowid

    # Update PhotoID in Recipe table
    cursor.execute("UPDATE Recipe SET PhotoID = %s WHERE ID = %s", (photo_id, recipe_id))

    # Insert into Ingredients table
    for i in range(len(ingredients_name)):
        cursor.execute("INSERT INTO Ingredients (IngredientName, Instruction, Quantity, Unit, Category) VALUES (%s, %s, %s, %s, %s)",
                       (ingredients_name[i], instructions[i], quantities[i], units[i], categories[i]))
        ingredient_id = cursor.lastrowid
        # Insert into xRecipeIngredients table
        cursor.execute("INSERT INTO xRecipeIngredients (RecipeID, IngredientID) VALUES (%s, %s)", (recipe_id, ingredient_id))

    # Insert into Steps table
    for i in range(len(steps)):
        cursor.execute("INSERT INTO Steps (StepText, StepNumber) VALUES (%s, %s)", (steps[i], i + 1))
        step_id = cursor.lastrowid
        # Insert into xRecipeSteps table
        cursor.execute("INSERT INTO xRecipeSteps (RecipeID, StepsID) VALUES (%s, %s)", (recipe_id, step_id))

    connection.commit()
    cursor.close()

    flash('Recipe saved successfully!', 'success')
    # Redirect to view the saved recipe
    return redirect(url_for('views.view_recipe', recipe_id=recipe_id))

@views.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    cursor = connection.cursor(dictionary=True)

    # Fetch recipe details including photo ID
    cursor.execute("SELECT * FROM Recipe WHERE ID = %s", (recipe_id,))
    recipe = cursor.fetchone()

    if recipe:
        # Fetch tags associated with the recipe
        cursor.execute("""
            SELECT Tags.TagName
            FROM Tags
            INNER JOIN xRecipeTags ON Tags.ID = xRecipeTags.TagID
            WHERE xRecipeTags.RecipeID = %s
        """, (recipe_id,))
        tags = [tag['TagName'] for tag in cursor.fetchall()]

        # Fetch ingredients for the recipe
        cursor.execute("""
            SELECT Ingredients.IngredientName, Ingredients.Instruction, Ingredients.Quantity, Ingredients.Unit, Ingredients.Category
            FROM Ingredients
            INNER JOIN xRecipeIngredients ON Ingredients.ID = xRecipeIngredients.IngredientID
            WHERE xRecipeIngredients.RecipeID = %s
        """, (recipe_id,))
        ingredients = cursor.fetchall()

        # Group ingredients by category
        ingredients_by_category = {}
        for ingredient in ingredients:
            category = ingredient['Category']
            if category not in ingredients_by_category:
                ingredients_by_category[category] = []
            ingredients_by_category[category].append(ingredient)

        # Fetch steps for the recipe
        cursor.execute("""
            SELECT Steps.StepText
            FROM Steps
            INNER JOIN xRecipeSteps ON Steps.ID = xRecipeSteps.StepsID
            WHERE xRecipeSteps.RecipeID = %s
            ORDER BY xRecipeSteps.ID
        """, (recipe_id,))
        steps = [step['StepText'] for step in cursor.fetchall()]

        # Fetch future weeks available in the database
        cursor.execute("SELECT DISTINCT WeekNumber FROM MealPlans WHERE StartDate >= CURDATE()")
        future_weeks = [week['WeekNumber'] for week in cursor.fetchall()]

        # Fetch photo data based on the photo ID from the recipe
        cursor.execute("SELECT Photo FROM Photos WHERE ID = %s", (recipe['PhotoID'],))
        photo_data = cursor.fetchone()['Photo'] if recipe['PhotoID'] else None

        # Convert photo from bytes to base64
        photo_data_base64 = base64.b64encode(photo_data).decode('utf-8') if photo_data else None

        cursor.close()

        return render_template('recipe.html', recipe=recipe, tags=tags, ingredients_by_category=ingredients_by_category, steps=steps, future_weeks=future_weeks, photo_data_base64=photo_data_base64)
    else:
        # Recipe not found, handle error (e.g., display a message or redirect)
        flash('Recipe not found!', 'error')
        return redirect(url_for('views.index'))  # Assuming you have an index route






@views.route('/recipe/<int:recipe_id>/edit')
def edit_recipe(recipe_id):
    cursor = connection.cursor(dictionary=True)
    
    # Fetch recipe details
    cursor.execute("SELECT * FROM Recipe WHERE ID = %s", (recipe_id,))
    recipe = cursor.fetchone()

    # Fetch tags associated with the recipe
    cursor.execute("""
        SELECT Tags.TagName
        FROM Tags
        INNER JOIN xRecipeTags ON Tags.ID = xRecipeTags.TagID
        WHERE xRecipeTags.RecipeID = %s
    """, (recipe_id,))
    tags = [tag['TagName'] for tag in cursor.fetchall()]

    # Fetch ingredients for the recipe
    cursor.execute("""
        SELECT Ingredients.IngredientName, Ingredients.Instruction, Ingredients.Quantity, Ingredients.Unit, Ingredients.Category
        FROM Ingredients
        INNER JOIN xRecipeIngredients ON Ingredients.ID = xRecipeIngredients.IngredientID
        WHERE xRecipeIngredients.RecipeID = %s
    """, (recipe_id,))
    ingredients = cursor.fetchall()

    # Fetch steps for the recipe
    cursor.execute("""
        SELECT Steps.StepText
        FROM Steps
        INNER JOIN xRecipeSteps ON Steps.ID = xRecipeSteps.StepsID
        WHERE xRecipeSteps.RecipeID = %s
        ORDER BY xRecipeSteps.ID
    """, (recipe_id,))
    steps = [step['StepText'] for step in cursor.fetchall()]

    cursor.close()

    return render_template('edit_recipe.html', recipe=recipe, tags=tags, ingredients=ingredients, steps=steps)

@views.route('/update-recipe/<int:recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    cursor = connection.cursor()

    # Retrieve existing recipe details from the database
    cursor.execute("SELECT * FROM Recipe WHERE ID = %s", (recipe_id,))
    existing_recipe = cursor.fetchone()

    if request.method == 'POST':
        # Extract data from the form
        recipe_name = request.form.get('recipe_name')
        description = request.form.get('description')
        url = request.form.get('url')
        oven_temp = request.form.get('oven_temp')
        time = request.form.get('time')
        tags = request.form.getlist('tags')
        photo = request.files.get('photo')

        # Compare form data with existing recipe data and update if necessary
        if recipe_name != existing_recipe['RecipeName']:
            cursor.execute("UPDATE Recipe SET RecipeName = %s WHERE ID = %s", (recipe_name, recipe_id))

        if description != existing_recipe['Description']:
            cursor.execute("UPDATE Recipe SET Description = %s WHERE ID = %s", (description, recipe_id))

        if url != existing_recipe['URL']:
            cursor.execute("UPDATE Recipe SET URL = %s WHERE ID = %s", (url, recipe_id))

        if oven_temp != existing_recipe['OvenTemp']:
            cursor.execute("UPDATE Recipe SET OvenTemp = %s WHERE ID = %s", (oven_temp, recipe_id))

        if time != existing_recipe['Time']:
            cursor.execute("UPDATE Recipe SET Time = %s WHERE ID = %s", (time, recipe_id))

        # Handle tags separately if needed

        # Commit changes and close cursor
        connection.commit()
        cursor.close()

        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('views.view_recipe', recipe_id=recipe_id))

    else:
        # Fetch tags list from the database
        cursor.execute("SELECT * FROM Tag")
        tags = cursor.fetchall()

        # Render the template with existing recipe data and tags
        return render_template('update_recipe.html', recipe=existing_recipe, tags=tags)


@views.route('/search')
def search():
    # Get the search query from the URL parameters
    search_query = request.args.get('query')

    # Initialize an empty list to store search results
    recipes = []

    if search_query:
        # Fetch recipes from the database that contain the search query in their names, ingredients, or tags
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT Recipe.*, Photos.Photo
            FROM Recipe
            LEFT JOIN Photos ON Recipe.PhotoID = Photos.ID
            LEFT JOIN xRecipeIngredients ON Recipe.ID = xRecipeIngredients.RecipeID
            LEFT JOIN Ingredients ON xRecipeIngredients.IngredientID = Ingredients.ID
            LEFT JOIN xRecipeTags ON Recipe.ID = xRecipeTags.RecipeID
            LEFT JOIN Tags ON xRecipeTags.TagID = Tags.ID
            WHERE RecipeName LIKE %s 
            OR IngredientName LIKE %s 
            OR TagName LIKE %s
        """, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        recipes_data = cursor.fetchall()

        for recipe_data in recipes_data:
            # Convert photo data to base64 encoding
            if recipe_data['Photo']:
                recipe_data['Photo'] = base64.b64encode(recipe_data['Photo']).decode('utf-8')

            recipes.append(recipe_data)

        cursor.close()

    # Render the search results page with the found recipes
    return render_template('search.html', recipes=recipes)

@views.route('/search_recipes')
def search_recipes():
    # Get the search query from the URL parameters
    search_query = request.args.get('query')

    # Initialize an empty list to store search results
    recipes = []

    if search_query:
        # Fetch recipes from the database that contain the search query in their names, ingredients, or tags
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT Recipe.*, Photos.Photo
            FROM Recipe
            LEFT JOIN Photos ON Recipe.PhotoID = Photos.ID
            LEFT JOIN xRecipeIngredients ON Recipe.ID = xRecipeIngredients.RecipeID
            LEFT JOIN Ingredients ON xRecipeIngredients.IngredientID = Ingredients.ID
            LEFT JOIN xRecipeTags ON Recipe.ID = xRecipeTags.RecipeID
            LEFT JOIN Tags ON xRecipeTags.TagID = Tags.ID
            WHERE RecipeName LIKE %s 
            OR IngredientName LIKE %s 
            OR TagName LIKE %s
        """, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        recipes_data = cursor.fetchall()

        for recipe_data in recipes_data:
            # Convert photo data to base64 encoding
            if recipe_data['Photo']:
                recipe_data['Photo'] = base64.b64encode(recipe_data['Photo']).decode('utf-8')

            recipes.append(recipe_data)

        cursor.close()

    # Render the recipe listing page with the found recipes
    return render_template('recipe_listing.html', recipes=recipes)


@views.route('/tags', methods=['GET'])
def tags():
    # Fetch tag names from the database
    cursor = connection.cursor()
    cursor.execute("SELECT TagName FROM Tags ORDER BY TagName ASC")  # ASC for ascending order
    tag_names = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Pass tag names to the HTML template
    return render_template("tags.html", tag_names=tag_names)


@views.route('/tag/<string:tag_name>')
def recipes_by_tag(tag_name):
    cursor = connection.cursor(dictionary=True)

    # Fetch recipes associated with the tag including photo data
    cursor.execute("""
        SELECT Recipe.*, Photos.Photo
        FROM Recipe
        INNER JOIN xRecipeTags ON Recipe.ID = xRecipeTags.RecipeID
        INNER JOIN Tags ON xRecipeTags.TagID = Tags.ID
        LEFT JOIN Photos ON Recipe.PhotoID = Photos.ID
        WHERE Tags.TagName = %s
    """, (tag_name,))
    recipes = cursor.fetchall()

    # Convert photo data to Base64 encoding
    for recipe in recipes:
        if recipe.get('Photo'):
            recipe['Photo'] = base64.b64encode(recipe['Photo']).decode('utf-8')

    cursor.close()

    return render_template('recipes_by_tag.html', tag_name=tag_name, recipes=recipes)



@views.route('/add_tag', methods=['POST'])
def add_tag():
    # Get the tag name from the request form
    tag_name = request.form.get('tag_name')

    if not tag_name:
        flash('Tag name cannot be empty!', 'error')
    else:
        # Check if the tag already exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Tags WHERE TagName = %s", (tag_name,))
        existing_tag = cursor.fetchone()
        cursor.close()

        if existing_tag:
            flash('Tag already exists!', 'error')
        else:
            # Insert the new tag into the database
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Tags (TagName) VALUES (%s)", (tag_name,))
            connection.commit()
            cursor.close()
            flash('Tag added successfully!', 'success')

    return redirect(url_for('views.tags'))

@views.route('/check_tag', methods=['POST'])
def check_tag():
    # Get the tag name from the AJAX request
    tag_name = request.json.get('tag_name')

    # Check if the tag exists in the database
    cursor = connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM Tags WHERE TagName = %s)", (tag_name,))
    tag_exists = cursor.fetchone()[0]
    cursor.close()

    # Return JSON response indicating whether the tag exists or not
    return jsonify({'exists': tag_exists})

@views.route('/delete_tag', methods=['POST'])
def delete_tag():
    # Get the tag name from the AJAX request
    tag_name = request.json.get('tag_name')

    try:
        # Delete the tag from the database
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Tags WHERE TagName = %s", (tag_name,))
        connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print(e)  # Log the error for debugging
        return jsonify({'success': False})


@views.route('/meal-planner')
def mealPlanner():
    # Get the current date
    current_datetime = datetime.now()

    # Calculate the current week number using the custom function
    current_week = get_week_number(current_datetime)

    # Query the database for all meal plans starting from the current week
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM MealPlans ORDER BY StartDate")
    meal_plans = cursor.fetchall()

    # Filter meal plans to exclude those with end date in the past
    meal_plans = [meal_plan for meal_plan in meal_plans if meal_plan['EndDate'] >= current_datetime.date()]

    # Find the previous week to highlight
    previous_week = current_week - 1

    # Fetch associated recipes for each meal plan from MealPlanRecipes table
    for meal_plan in meal_plans:
        cursor.execute("""
            SELECT Recipe.*, Photos.Photo AS RecipePhoto
            FROM Recipe
            INNER JOIN MealPlanRecipes ON Recipe.ID = MealPlanRecipes.RecipeID
            INNER JOIN Photos ON Recipe.PhotoID = Photos.ID
            WHERE MealPlanRecipes.MealPlanID = %s
        """, (meal_plan['ID'],))
        recipes = cursor.fetchall()
        # Decode base64 encoded photo data
        for recipe in recipes:
            recipe['RecipePhoto'] = base64.b64encode(recipe['RecipePhoto']).decode('utf-8')
        meal_plan['recipes'] = recipes

        # Print the current_week and week_number for debugging
        print("Current Week:", current_week)
        print("Week Number from Database:", meal_plan['WeekNumber'])

    cursor.close()

    # Render the meal planner template with the fetched meal plans, current date, and previous week highlighted
    return render_template('mealplanner.html', meal_plans=meal_plans, current_date=current_datetime.date(), current_week=previous_week)



@views.route('/remove-recipe/<int:recipe_id>/week/<int:week_number>', methods=['POST'])
def remove_recipe_from_week(recipe_id, week_number):
    # Define the SQL query to delete the recipe from the meal plan for the given week
    delete_query = "DELETE FROM MealPlanRecipes WHERE MealPlanID = (SELECT ID FROM MealPlans WHERE WeekNumber = %s) AND RecipeID = %s"

    # Execute the SQL query
    cursor = connection.cursor()
    cursor.execute(delete_query, (week_number, recipe_id))
    connection.commit()

    # Close the cursor (the connection will be closed automatically at the end of the request)
    cursor.close()

    # Redirect back to the meal planner page after the removal
    return redirect(url_for('views.mealPlanner'))





@views.route('/add-week-to-meal-planner', methods=['POST'])
def add_week_to_meal_planner():
    # Get the start date of the new week from the form
    start_date_str = request.form.get('start_date')
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    # Calculate the end date of the new week (assuming a week is 7 days)
    end_date = start_date + timedelta(days=6)

    # Determine the week number (based on ISO 8601 week date)
    week_number = start_date.isocalendar()[1]

    # Determine the year
    year = start_date.year

    # Insert the new week into the database
    cursor = connection.cursor()
    cursor.execute("INSERT INTO MealPlans (WeekNumber, Year, StartDate, EndDate) VALUES (%s, %s, %s, %s)", (week_number, year, start_date, end_date))
    connection.commit()
    cursor.close()

    # Redirect back to the meal planner page
    return redirect(url_for('views.mealPlanner'))


@views.route('/add-to-meal-planner', methods=['POST'])
def add_to_meal_planner():
    # Get the recipe ID and week number from the form
    recipe_id = request.form.get('recipe_id')
    week_number = request.form.get('week_number')

    # Get the current date
    current_datetime = datetime.now()
    current_week_number = current_datetime.isocalendar()[1]

    # Ensure that the selected week is in the future and available in the database
    if int(week_number) >= current_week_number:
        # Insert the recipe into the meal planner for the specified week
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO MealPlanRecipes (MealPlanID, RecipeID)
            SELECT ID, %s
            FROM MealPlans
            WHERE WeekNumber = %s
        """, (recipe_id, week_number))
        connection.commit()
        cursor.close()

        flash('Recipe added to the meal planner successfully!', 'success')
    else:
        flash('Invalid week selected. Please select a week in the future.', 'error')

    # Redirect back to the meal planner page
    return redirect(url_for('views.mealPlanner'))





@views.route('/recipe-listing/<int:week_number>')
def recipe_listing(week_number):
    # Fetch all recipes from the database
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT Recipe.*, Photos.Photo FROM Recipe LEFT JOIN Photos ON Recipe.PhotoID = Photos.ID")
    recipes = cursor.fetchall()
    cursor.close()

    # Encode photo data to base64 format
    for recipe in recipes:
        if recipe['Photo']:
            recipe['Photo'] = base64.b64encode(recipe['Photo']).decode('utf-8')

    # Get the search query from the URL query string
    search_query = request.args.get('search_query')

    # Filter recipes by name or tags if provided
    if search_query:
        # Fetch recipes matching the search query in name or tags
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT Recipe.*, Photos.Photo
            FROM Recipe
            LEFT JOIN xRecipeTags ON Recipe.ID = xRecipeTags.RecipeID
            LEFT JOIN Tags ON xRecipeTags.TagID = Tags.ID
            LEFT JOIN Photos ON Recipe.PhotoID = Photos.ID
            WHERE Recipe.RecipeName LIKE %s 
            OR Tags.TagName LIKE %s
        """, ('%' + search_query + '%', '%' + search_query + '%'))
        filtered_recipes = cursor.fetchall()
        cursor.close()

        # Encode photo data to base64 format for filtered recipes
        for recipe in filtered_recipes:
            if recipe['Photo']:
                recipe['Photo'] = base64.b64encode(recipe['Photo']).decode('utf-8')

        recipes = filtered_recipes

    return render_template('recipe_listing.html', recipes=recipes, week_number=week_number)






@views.route('/add_recipe_to_meal_planner/<int:recipe_id>/<int:week_number>', methods=['POST'])
def add_recipe_to_meal_planner(recipe_id, week_number):
    # Get the current date and year
    current_date = datetime.now()
    year = current_date.year

    # Determine the start date of the specified week
    start_date = datetime.strptime(f'{year}-W{week_number}-1', "%Y-W%W-%w").date()

    # Insert the recipe into the meal planner for the specified week
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO MealPlanRecipes (MealPlanID, RecipeID)
        SELECT ID, %s
        FROM MealPlans
        WHERE WeekNumber = %s AND YEAR(StartDate) = %s
    """, (recipe_id, week_number, year))
    connection.commit()
    cursor.close()

    # Redirect back to the meal planner page
    return redirect(url_for('views.mealPlanner'))

@views.route('/shopping-lists')
def shopping_lists():
    cursor = connection.cursor(dictionary=True)

    # Fetch meal plans for future weeks
    cursor.execute("SELECT * FROM MealPlans WHERE StartDate >= CURDATE()")
    meal_plans = cursor.fetchall()

    shopping_list = []

    # Iterate over each meal plan
    for meal_plan in meal_plans:
        # Fetch recipes associated with the meal plan
        cursor.execute("""
            SELECT Recipe.ID as RecipeID, Recipe.RecipeName, Ingredients.IngredientName, Ingredients.Quantity, Ingredients.Unit
            FROM Recipe
            INNER JOIN xRecipeIngredients ON Recipe.ID = xRecipeIngredients.RecipeID
            INNER JOIN Ingredients ON xRecipeIngredients.IngredientID = Ingredients.ID
            INNER JOIN MealPlanRecipes ON Recipe.ID = MealPlanRecipes.RecipeID
            WHERE MealPlanRecipes.MealPlanID = %s
        """, (meal_plan['ID'],))
        recipe_ingredients = cursor.fetchall()

        # Group ingredients by recipe name
        grouped_ingredients = {}
        for ingredient in recipe_ingredients:
            recipe_name = ingredient['RecipeName']
            if recipe_name not in grouped_ingredients:
                grouped_ingredients[recipe_name] = []
            grouped_ingredients[recipe_name].append(ingredient)

        # Append week number, start date, and grouped ingredients to the shopping list
        shopping_list.append({
            'WeekNumber': meal_plan['WeekNumber'],
            'StartDate': meal_plan['StartDate'],
            'RecipeIngredients': grouped_ingredients
        })

    cursor.close()
    
    # Get the current date
    current_datetime = datetime.now()

    # Calculate the current week number using the custom function
    current_week = get_week_number(current_datetime)

    return render_template('shopping_lists.html', shopping_list=shopping_list, current_week=current_week)

