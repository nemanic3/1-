from django.db import models
from django.core.validators import RegexValidator

class User(models.Model):
    # 영어 1자 + 숫자 6자리 (예: C135195)
    student_id = models.CharField(
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z]\d{6}$',
                message='학번은 영문자 1자와 숫자 6자리여야 합니다. (예: C135195)'
            )
        ]
    )
    # 한글만 2~5자
    full_name = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(
                regex=r'^[가-힣]{2,5}$',
                message='이름은 한글 2~5자만 입력 가능합니다.'
            )
        ]
    )
    # 입학년도
    entry_year = models.PositiveSmallIntegerField()

    # 전공
    major = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
