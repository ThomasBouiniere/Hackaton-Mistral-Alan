import os
import sys
import django
import json
from django.db import transaction

sys.path.append('/code')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from models.models import Recipe, Ingredient, IngredientQuantity, Allergen, IngredientAllergen
from models.constants import ALLERGEN_CHOICES, RECIPE_CHOICES

with open("populate_db_sql/data/to_populate.json") as file:
    data = json.load(file)

def check_recipe(recipe_name):
    return not Recipe.objects.filter(name=recipe_name).exists()

def check_ingredient(nutrional_values):
    is_valid = True
    for value in nutrional_values:
        is_valid = is_valid and (value >= 0)
    return is_valid

def check_allergen(allergen):
    return allergen in ALLERGEN_CHOICES

def check_type(type):
    return type in RECIPE_CHOICES

def clean_quantity(quantity):
    if "tbsp" in quantity or "tsp" in quantity or "cloves" in quantity:
        return 5* float(quantity.replace(" tbsp", "g").replace(" tsp", "g").replace(" cloves", "g")[:-1].replace("g", ""))
    return float(quantity.replace("ml", "g")[:-1].replace("g", ""))

def populate_database():
    for recipe_data in data["recipes"]:
        try:
            with transaction.atomic():
                is_valid = True

                recipe_name = recipe_data["name"]
                ingredients = recipe_data["ingredients"]
                steps = recipe_data["steps"]
                is_valid = is_valid and check_recipe(recipe_name=recipe_name)
                type = recipe_data["type"]
                is_valid = is_valid and check_type(type=type)
                for ingredient in ingredients:
                    ingredient_name = ingredient["name"]
                    ingredient_quantity = clean_quantity(ingredient["amount"])
                    calories = ingredient["nutritional_value"]["calories"]
                    fiber = float(ingredient["nutritional_value"]["fiber"][:-1].replace("g", ""))
                    saturated_fatty_acids = float(ingredient["nutritional_value"]["saturated_fatty_acids"][:-1].replace("g", ""))
                    carbohydrates = float(ingredient["nutritional_value"]["carbohydrates"][:-1].replace("g", ""))
                    proteins = float(ingredient["nutritional_value"]["proteins"][:-1].replace("g", ""))
                    allergens = ingredient["allergens"]
                    is_valid = is_valid and check_ingredient(nutrional_values=[
                                                                ingredient_quantity,
                                                                calories,
                                                                fiber,
                                                                saturated_fatty_acids,
                                                                carbohydrates,
                                                                proteins,
                                                            ])
                    print(is_valid)
                    if allergens is not None:
                        for allergen in allergens:
                            is_valid = is_valid and check_allergen(allergen)
                
                if not is_valid:
                    continue

                recipe = Recipe.objects.create(
                    name=recipe_name,
                    type=type,
                    instructions=steps,
                )

                for ingredient in ingredients:
                    ingredient_name = ingredient["name"]
                    ingredient_quantity = clean_quantity(ingredient["amount"])
                    calories = ingredient["nutritional_value"]["calories"]
                    fiber = float(ingredient["nutritional_value"]["fiber"][:-1])
                    saturated_fatty_acids = float(ingredient["nutritional_value"]["saturated_fatty_acids"][:-1])
                    carbohydrates = float(ingredient["nutritional_value"]["carbohydrates"][:-1])
                    proteins = float(ingredient["nutritional_value"]["proteins"][:-1])
                    allergens = ingredient["allergens"]

                    if Ingredient.objects.filter(name=ingredient_name).exists():
                        ingredient = Ingredient.objects.get(name=ingredient_name)
                    else:
                        ingredient = Ingredient.objects.create(
                            name=ingredient_name,
                            protein=proteins,
                            fiber=fiber,
                            carbohydrate=carbohydrates,
                            calories=calories,
                            saturated_fatty_acid=saturated_fatty_acids,
                        )
                        if allergens is not None:
                            for allergen in allergens:
                                allergen, _ = Allergen.objects.get_or_create(
                                    name=allergen
                                )
                                IngredientAllergen.objects.create(
                                    ingredient=ingredient,
                                    allergen=allergen
                                )

                    IngredientQuantity.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=ingredient_quantity
                    )

            print("Database populated successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    populate_database()