import os
import sys
import django

sys.path.append('/code')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from models.models import Recipe, RecipeVector
from populate_db_vector.from_sql.processing import from_recipe_sql_to_text

from dotenv import load_dotenv
from mistralai import Mistral


load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)

def get_text_embedding(inputs):
    embeddings_batch_response = client.embeddings.create(
        model=model,
        inputs=inputs
    )
    return embeddings_batch_response.data[0].embedding

def populate_database():
    for recipe in Recipe.objects.all():
        recipe_text = from_recipe_sql_to_text(recipe_sql=recipe)
        embedding_vector = get_text_embedding(recipe_text)
        if not RecipeVector.objects.filter(recipe=recipe).exists():
            RecipeVector.objects.create(
                recipe=recipe,
                embedded_recipe=embedding_vector,
            )
    return

if __name__ == '__main__':
    populate_database()