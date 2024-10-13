# my_app/urls.py
from django.urls import path
from .views import process_question

app_name = 'llm_response'

urlpatterns = [
    path('process_question/', process_question, name='process_question'),
    path('question/', process_question, name='question_form')
]
