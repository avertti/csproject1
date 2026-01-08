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

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        if question.access_code and not request.session.get(f"access_{question.pk}"):
            return HttpResponseRedirect(reverse("polls:access", args=(question.pk,)))
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # Flaw 3: CSRF, Accepts GET for voting
    try:
        choice_id = request.GET.get("choice") or request.POST.get("choice")
        selected_choice = question.choice_set.get(pk=choice_id)
    # Fix 3:
    # Only allow POST requests
    # try:
    #    selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
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


# Flaw 2: Broken Access Control AO1


def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user_id = request.GET.get("user_id") or request.POST.get("user_id")

    if (
        user_id
        and question.owner
        and (str(question.owner.id) == user_id or request.user.is_staff)
    ):
        if request.method == "POST":
            question.delete()
            return HttpResponseRedirect(reverse("polls:index"))
        return render(
            request,
            "polls/delete_confirm.html",
            {"question": question, "user_id": user_id},
        )

    return HttpResponseRedirect(reverse("polls:index"))

    # Fix 2:
    # from django.contrib.auth.decorators import login_required
    # from django.http import HttpResponseForbidden

    # @login_required
    # def delete_question(request, question_id):
    #       question = get_object_or_404(Question, pk=question_id)

    #       if question.owner != request.user and not request.user.is_staff:
    #           return HttpResponseForbidden("You can't delete this question.")

    #       if request.method == "POST":
    #           question.delete()
    #           return HttpResponseRedirect(reverse("polls:index"))

    #       return render(request, "polls/delete_confirm.html", {"question": question})

    # def access_code_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.access_code:
        return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))

    if request.method == "POST":
        entered_code = request.POST.get("access_code", "")
        # Flaw 4: Direct plaintext comparison
        if entered_code == question.access_code:
            request.session[f"access_{question_id}"] = True
            return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))
        else:
            return render(
                request,
                "polls/access.html",
                {"question": question, "error": "Invalid access code"},
            )

    return render(request, "polls/access.html", {"question": question})


# Fix 4:
from django.contrib.auth.hashers import check_password


def access_code_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.access_code:
        return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))

    if request.method == "POST":
        entered_code = request.POST.get("access_code", "")

        if entered_code and check_password(entered_code, question.access_code):
            request.session[f"access_{question_id}"] = True
            return HttpResponseRedirect(reverse("polls:detail", args=(question_id,)))
        else:
            return render(
                request,
                "polls/access.html",
                {"question": question, "error": "Invalid access code"},
            )
    return render(request, "polls/access.html", {"question": question})
