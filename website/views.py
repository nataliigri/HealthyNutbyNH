from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from . import db
from .models import Recipe, Ingredient, Step, WeekDay, WeeklyMealPlan, RecipeIngredient, recipe_weekday
from slugify import slugify
from flask import flash
from sqlalchemy.orm.exc import StaleDataError

from werkzeug.exceptions import abort

import json


views = Blueprint('views', __name__)

day_names = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday'
}

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html')

@views.route('/creatingrecipes', methods=['GET', 'POST'])  
def create_recipe():
    if request.method == 'POST':
        # Отримати дані з форми
        title = request.form.get('title')
        # Перевірити чи поле 'title' заповнене
        if not title:
            return render_template('creating_recipes.html', error='Please enter a title')
            raise ValueError('Please enter a title')
        slug = slugify(title)
        description = request.form.get('description')
        if not description:
            return render_template('creating_recipes.html', error='Please enter description')
            raise ValueError('Please enter a description')
        image_filename = request.form.get('image_filename')
        cooking_time = request.form.get('cooking_time')
        if not cooking_time:
            return render_template('creating_recipes.html', error='Please enter a cooking time')
        if not cooking_time.isdigit():
            return render_template('creating_recipes.html', error='Cooking time should be a number')
        weekday_ids = request.form.getlist('weekday_id')
        if not weekday_ids:
            return render_template('creating_recipes.html', error='Please select at least one weekday')
       
        # Створити новий рецепт
        recipe = Recipe(slug=slug, title=title, description=description,
                        image_filename=image_filename, cooking_time=cooking_time)

        # Додати рецепт до бази даних
        db.session.add(recipe)
        db.session.commit()

        # Створити нові кроки
        steps = []
        for i in range(1, 6):
            description = request.form.get(f'step_description_{i}')
            if description:
                step = Step(step_number=i, step_description=description, recipe_id=recipe.id)
                steps.append(step)

        if not steps:
            return render_template('creating_recipes.html', error='Recipe must have at least one step')
            raise ValueError('Please enter a title')
           
        for step in steps:
            db.session.add(step)
        db.session.commit()

        # Створити нові інгредієнти
        ingredients = []
        recipe_ingredients = []
        for i in range(3):
            name = request.form.getlist('ingredient_name[]')[i]
            quantity = request.form.getlist('ingredient_quantity[]')[i]
            unit = request.form.getlist('ingredient_unit[]')[i]

            if name and quantity and unit:
                # Retrieve the Ingredient object from the database
                ingredient = Ingredient.query.filter_by(name=name).first()
                if ingredient is None:
                    ingredient = Ingredient(name=name)
                    db.session.add(ingredient)
                    db.session.commit()
                ingredients.append(ingredient)

                # Create the recipe_ingredient object and append it to the list
                recipe_ingredient = RecipeIngredient(quantity=quantity, unit=unit, recipe_id=recipe.id, ingredient_id=ingredient.id)
                recipe.recipe_ingredients.append(recipe_ingredient)

        if not ingredients:
            raise ValueError("Recipe must have at least one ingredient.")
        for ingredient in ingredients:
            db.session.add(ingredient)
        for recipe_ingredient in recipe_ingredients:
            db.session.add(recipe_ingredient)
        db.session.commit()

  

        # Додати кроки до рецепту
        for step in steps:
            step.recipe_id = recipe.id
            db.session.add(step)

        # Додати інгредієнти до рецепту
        for recipe_ingredient_obj in recipe_ingredients:
            recipe.recipe_ingredients.append(recipe_ingredient_obj)

        # Отримати WeeklyMealPlan з бази даних
        weeklymealplan = WeeklyMealPlan.query.get(1)
        if not weeklymealplan:
            # Якщо WeeklyMealPlan не існує, створити новий
            weeklymealplan = WeeklyMealPlan(id=1, slug="weekly_meal_plan")
            db.session.add(weeklymealplan)
            db.session.commit()
    
        for weekday_id in weekday_ids:
            day_name = day_names.get(int(weekday_id))
            weekday = WeekDay.query.filter_by(day_name=day_name, weeklymealplan_id=weeklymealplan.id).first()
            if not weekday:
                weekday = WeekDay(day_name=day_name, weeklymealplan_id=weeklymealplan.id)
                db.session.add(weekday)
                db.session.commit()

            # Add the recipe to the WeekDay object
            weekday.recipe_weekdays.append(recipe)
            db.session.commit()

        return redirect(url_for('views.view_recipe', slug=slug))
    else:
        return render_template('creating_recipes.html')


@views.route('/recipe/<slug>')
def view_recipe(slug):
    recipe = Recipe.query.filter_by(slug=slug).first_or_404()
    ingredients = Ingredient.query.all()
    return render_template('recipe.html', recipe=recipe,ingredients=ingredients)

@views.route('/weekly_meal_plan')
def weekly_meal_plan():
    weekdays = WeekDay.query.all()
    return render_template('weekly_meal_plan.html', weekdays=weekdays)

@views.route('/recipes',methods=['GET', 'POST'])
def recipes():
    recipes = Recipe.query.all()
    #return render_template('all_recipes.html', recipes=recipes)
    
    recipe_dicts = [recipe.to_dict() for recipe in recipes]
    return jsonify(recipe_dicts)
    


@views.route('/add_to_planner', methods=['GET', 'POST'])
def add_to_planner():
    # Отримати дані з запиту
    recipe_id = request.form.get('recipe_id')
    days_of_week = request.form.getlist('days_of_week[]')
    if not recipe_id or not days_of_week:
        abort(400)

    # Знайти рецепт за ID
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        abort(404)

    # Знайти дні тижня за назвами
    weekdays = WeekDay.query.filter(WeekDay.day_name.in_(days_of_week)).all()

    # Перевірити, чи рецепт ще не додано до цих днів тижня
    for weekday in weekdays:
        if recipe in weekday.recipe_weekdays:
            abort(400)

    # Додати рецепт до щотижневого плану харчування
    for weekday in weekdays:
        weekday.recipe_weekdays.append(recipe)

    db.session.commit()


    return redirect(url_for('views.recipes'))

@views.route('/recipes/delete/<int:recipe_id>', methods=('POST',))
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        # delete associated recipe_ingredient rows
        for ri in recipe.recipe_ingredients:
            db.session.delete(ri)
        db.session.commit()
        

        # Видаляємо записи з таблиці зв'язку
        recipe.weekdays.clear()
        db.session.commit()

        # Видаляємо сам запис
        db.session.delete(recipe)
        db.session.commit()

    return redirect(url_for('views.recipes'))
