from django.db import models


class Question(models.Model):
    TYPE_DO = 1
    TYPE_AM = 2
    TYPE_IN = 3
    TYPES = (
        (TYPE_DO, 'type_do'),
        (TYPE_AM, 'type_am'),
        (TYPE_IN, 'type_in'),
    )

    type_question = models.PositiveSmallIntegerField(
        choices=TYPES, null=True)
    question_text = models.CharField(max_length=200)
    answer_text = models.CharField(max_length=200)


class UsersQuestion(models.Model):
    used_id = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
