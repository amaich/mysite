from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

import datetime

from .models import Question, Choice

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=30, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(new_question_text, offset_days):
    time = timezone.now() + datetime.timedelta(days=offset_days)
    question = Question.objects.create(question_text=new_question_text, pub_date=time)
    choice = Choice.objects.create(question=question, choice_text='test')
    return question

def create_question_no_choice(new_question_text, offset_days):
    time = timezone.now() + datetime.timedelta(days=offset_days)
    return Question.objects.create(question_text=new_question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_question_no_choice(self):
        """
        If question with choices exist, an appropriate message is displayed.
        """
        create_question_no_choice("No choice question.", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_question_with_choice_and_no_choice(self):
        """
        Even if both no and with choice questions exist, only with choice questions
        are displayed.
        """
        question = create_question("With choice question.", -5)
        create_question_no_choice("No choice question", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )


    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question("Past question.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )
    
    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question("Past question.", -30)
        create_question("future_question", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question("Past question 1.", -30)
        question2 = create_question("Past question 2.", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question("Future question.", 5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question("Past question.", -5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_with_no_choice(self):
        """
        The detail view of a question with no choice foreign key
        displays the question's text.
        """
        no_choice_question = create_question_no_choice("No choice.", -5)
        url = reverse('polls:detail', args=(no_choice_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choice(self):
        """
        The detail view of a question with choice foreign key
        displays the question's text.
        """
        with_choice_question = create_question("with choice.", -5)
        url = reverse('polls:detail', args=(with_choice_question.id,))
        response = self.client.get(url)
        self.assertContains(response, with_choice_question.question_text)


class QuestionResultViewTests(TestCase):
    def test_future_question_result(self):
        """
        The result view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question("Future question.", 5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_result(self):
        """
        The result view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question("Past question.", -5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_question_with_no_choice(self):
        """
        The result view of a question with no choice foreign key
        displays the question's text.
        """
        no_choice_question = create_question_no_choice("No choice.", -5)
        url = reverse('polls:results', args=(no_choice_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choice(self):
        """
        The result view of a question with choice foreign key
        displays the question's text.
        """
        with_choice_question = create_question("with choice.", -5)
        url = reverse('polls:results', args=(with_choice_question.id,))
        response = self.client.get(url)
        self.assertContains(response, with_choice_question.question_text)