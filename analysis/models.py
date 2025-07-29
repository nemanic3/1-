from django.db import models

class GraduationRequirement(models.Model):
    major = models.CharField(max_length=100)       # 학과명
    year = models.PositiveSmallIntegerField()      # 입학년도 (예: 2025)

    total_required = models.IntegerField(default=132)
    major_required = models.IntegerField(default=50)
    general_required = models.IntegerField(default=8)
    drbol_required = models.IntegerField(default=18)
    special_general_required = models.IntegerField(default=3)
    sw_required = models.IntegerField(default=9)
    msc_required = models.IntegerField(default=23)

    major_must_courses = models.TextField(help_text="전공 필수 과목명(콤마 구분)")
    drbol_areas = models.TextField(help_text="드볼 영역 이름(콤마 구분)")

    class Meta:
        unique_together = ('major', 'year')

    def __str__(self):
        return f"{self.major} {self.year}학번 졸업 요건"
