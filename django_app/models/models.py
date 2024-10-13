from django.db import models
from django.db.models import Q
from models.constants import RECIPE_TYPE_CHOICES

from django.contrib.postgres.fields import ArrayField

class Allergen(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,  # Each allergen must be unique
        help_text="Allergen associated with the ingredient"
    )

    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,  # Each ingredient must have a unique name
        help_text="The name of the ingredient"
    )
    protein = models.FloatField(
        default=0,
        help_text="Amount of protein (in grams) per 100g of the ingredient"
    )
    fiber = models.FloatField(
        default=0,
        help_text="Amount of fiber (in grams) per 100g of the ingredient"
    )
    carbohydrate = models.FloatField(
        default=0,
        help_text="Amount of carbohydrates (in grams) per 100g of the ingredient"
    )
    calories = models.FloatField(
        default=0,
        help_text="Amount of calories (in kcal) per 100g of the ingredient"
    )
    saturated_fatty_acid = models.FloatField(
        default=0,
        help_text="Amount of saturated fatty acids (in grams) per 100g of the ingredient"
    )
    allergens = models.ManyToManyField(
        Allergen,
        through='IngredientAllergen',
        blank=True,
        help_text="Allergens associated with the ingredient"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(protein__gte=0) & Q(fiber__gte=0) & Q(carbohydrate__gte=0) & Q(calories__gte=0),
                name="positive_nutritional_values"
            )
        ]


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="The name of the recipe"
    )
    type = models.CharField(
        max_length=5,
        choices=RECIPE_TYPE_CHOICES,
        help_text="The type of the recipe (snack or meal)",
        default="meal",
    )
    image = models.URLField(
        help_text="The URL of the recipe image",
        blank=True,
        null=True
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientQuantity',
        help_text="The ingredients used in the recipe"
    )
    instructions = models.TextField(
        help_text="Instructions for preparing the recipe"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_recipe_name'),
        ]


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text="The recipe this ingredient belongs to"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text="The ingredient used in the recipe"
    )
    quantity = models.FloatField(
        help_text="Quantity of this ingredient in grams for the recipe"
    )

    def __str__(self):
        return f"{self.quantity}g of {self.ingredient.name} in {self.recipe.name}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(quantity__gte=0),
                name="positive_quantity"
            ),
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class IngredientAllergen(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.allergen.name} in {self.ingredient.name}"


class RecipeVector(models.Model):
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='vector',
        help_text="Reference to the associated recipe"
    )
    embedded_recipe = ArrayField(
        models.FloatField(),
        size=1024,
        help_text="Array of vector embeddings of the recipes",
    )
