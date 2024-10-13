import os
import sys
import django

sys.path.append('/code')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from models.models import IngredientQuantity, IngredientAllergen

def text_template(recipe_name, recipe_type, recipe_ingredients, nutritional_values, allergens):
    ingredients_list = ', '.join([f'{recipe_ingredients[ingredient]}g of {ingredient}' for ingredient in recipe_ingredients.keys()])
    nutritional_list = ', '.join([f'{nutritional_values[macro]}g of {macro}' for macro in nutritional_values.keys()])
    if allergens:
        allergens_list = 'the allergens are ' + ', '.join(allergens)
    else:
        allergens_list = 'no allergens are found'

    return (
        f"This recipe is for a {recipe_type}. It's called {recipe_name}. It requires {ingredients_list}."
        f" Therefore, it contains {nutritional_list} and {allergens_list}."
    )

def from_recipe_sql_to_text(recipe_sql):
    recipe_type = recipe_sql.type
    recipe_ingredients = {
        ingredient_quantity.ingredient.name: int(ingredient_quantity.quantity) for ingredient_quantity in IngredientQuantity.objects.filter(recipe=recipe_sql)
    }
    nutritional_values = {
        "calories": int(sum(q.ingredient.calories for q in IngredientQuantity.objects.filter(recipe=recipe_sql))),
        "proteins": int(sum(q.ingredient.protein for q in IngredientQuantity.objects.filter(recipe=recipe_sql))),
        "fibers": int(sum(q.ingredient.fiber for q in IngredientQuantity.objects.filter(recipe=recipe_sql))),
        "carbohydrates": int(sum(q.ingredient.carbohydrate for q in IngredientQuantity.objects.filter(recipe=recipe_sql))),
        "saturated_fatty_acids": int(sum(q.ingredient.saturated_fatty_acid for q in IngredientQuantity.objects.filter(recipe=recipe_sql)))
    }
    allergens = set(q.allergen.name for q in IngredientAllergen.objects.filter(
        ingredient__in=[q.ingredient for q in IngredientQuantity.objects.filter(recipe=recipe_sql)]
    ))
    if "None" in allergens:
        allergens.remove("None")
    return text_template(
        recipe_name=recipe_sql.name,
        recipe_type=recipe_type,
        recipe_ingredients=recipe_ingredients,
        nutritional_values=nutritional_values,
        allergens=allergens,
    )