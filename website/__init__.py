from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    ma = Marshmallow(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import  Step, Ingredient, WeekDay,Recipe, WeeklyMealPlan
    
    with app.app_context():
        db.create_all()
        '''
        # Створюємо новий рецепт
        new_recipe = Recipe(
            slug='pasta-with-tomato-sauce',
            title='Pasta with Tomato Sauce',
            description='A classic pasta dish with a rich tomato sauce.',
            image_filename='pasta.jpg',
            cooking_time=30,
            weekday_id=1,
            ingredients=[
                Ingredient(name='pasta', quantity=500, unit='g'),
                Ingredient(name='canned tomatoes', quantity=400, unit='g'),
            ],
            steps=[
                Step(step_number=1, step_description='Cook the pasta according to the package instructions.'),
                Step(step_number=2, step_description='Heat the canned tomatoes in a saucepan over medium heat.'),
            ]
        )

        # Додаємо рецепт до сесії та зберігаємо його
        db.session.add(new_recipe)
        db.session.commit()'''

    
    
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
    
