from . import db
from flask import jsonify

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer)
    step_description = db.Column(db.String(1000))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))


# Моделі з таблицею зв'язку
recipe_weekday = db.Table('recipe_weekday',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('weekday_id', db.Integer, db.ForeignKey('week_day.id'), primary_key=True)
)

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.String(64), nullable=False)
    unit = db.Column(db.String(64), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id',ondelete='CASCADE'), nullable=False)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50),unique=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(1000))
    image_filename = db.Column(db.String(100))
    steps = db.relationship('Step', backref='recipe')
    cooking_time = db.Column(db.Integer)
    weekdays = db.relationship('WeekDay', secondary='recipe_weekday', backref='meal_plans')
    recipe_ingredients = db.relationship('RecipeIngredient', backref='recipe')

    def to_dict(self):
        ingredients = []
        for ri in self.recipe_ingredients:
            ingredients.append({
                'quantity': ri.quantity,
                'unit': ri.unit,
            })
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'cooking_time': self.cooking_time,
            'recipe_ingredients': ingredients,
        }

class WeekDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_name = db.Column(db.String(80))
    recipe_weekdays = db.relationship('Recipe', secondary=recipe_weekday, backref='week_days')
    weeklymealplan_id = db.Column(db.Integer, db.ForeignKey('weekly_meal_plan.id'))

class WeeklyMealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50),unique=True)
    weekdays = db.relationship('WeekDay', backref='weekly_meal_plan')

