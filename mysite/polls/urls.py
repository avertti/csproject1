from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    # Flaw 1: SQL Injection vulnerable endpoint
    path("search/", views.search_questions, name="search"),
    # Flaw 2: Insecure direct object reference
    path("<int:question_id>/delete/", views.delete_question, name="delete"),
    # Flaw 4: Plaintext access code
    path("<int:question_id>/access/", views.access_code_poll, name="access"),
]
