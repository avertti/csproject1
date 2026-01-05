from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import connection

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date"
        )[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


# Flaw 1: Injection AO3
def search_questions(request):

    search_query = request.GET.get("q", "")

    with connection.cursor() as cursor:
        query = (
            "SELECT id, question_text, pub_date FROM polls_question WHERE question_text LIKE '%"
            + search_query
            + "%'"
        )
        cursor.execute(query)
        results = cursor.fetchall()

    # Fix 1:
    # with connection.cursor() as cursor:
    #     query = "SELECT id, question_text, pub_date FROM polls_question WHERE question_text LIKE %s"
    #     cursor.execute(query, [f"%{search_query}%"])
    #     results = cursor.fetchall()

    questions = []
    for row in results:
        questions.append({"id": row[0], "question_text": row[1], "pub_date": row[2]})

    return render(
        request,
        "polls/search_results.html",
        {"questions": questions, "search_query": search_query},
    )
