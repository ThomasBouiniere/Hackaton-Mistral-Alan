import os
import sys
import django

sys.path.append('/code')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from populate_db_vector.from_sql.processing import from_recipe_sql_to_text
from models.models import Recipe

res = ""

for recipe in Recipe.objects.all():
    res += from_recipe_sql_to_text(recipe_sql=recipe) + "/"

file_path = "populate_db_vector/data/recipes_output.txt"

with open(file_path, "w") as file:
    file.write(res)

print(f"Le texte des recettes a été sauvegardé dans {file_path}")