from django.db import models

class GraduationRequirement(models.Model):
    major = models.CharField(max_length=100)       # 학과명
    year = models.PositiveSmallIntegerField()      # 입학년도 (예: 2025)

    # 총 학점 요건
    total_required = models.IntegerField(default=132)
    major_required = models.IntegerField(default=50)
    general_required = models.IntegerField(default=8)
    drbol_required = models.IntegerField(default=18)
    special_general_required = models.IntegerField(default=3)
    sw_required = models.IntegerField(default=9)
    msc_required = models.IntegerField(default=23)

    # 전공 필수 / 전공 선택
    major_must_courses = models.JSONField(help_text="전공 필수 과목명 및 학기 정보(JSON 형태)")
    major_selective_courses = models.JSONField(help_text="전공 선택 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)

    # 교양 필수 / 교양 선택 / 특성화교양 / SW / MSC
    general_must_courses = models.JSONField(help_text="교양 필수 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)
    general_selective_courses = models.JSONField(help_text="일반선택 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)
    special_general_courses = models.JSONField(help_text="특성화교양 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)
    sw_courses = models.JSONField(help_text="SW/데이터활용역량 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)
    msc_courses = models.JSONField(help_text="MSC 과목명 및 학기 정보(JSON 형태)", null=True, blank=True)

    # 드볼
    drbol_areas = models.TextField(help_text="드볼 영역 이름(콤마 구분)")
    drbol_courses = models.JSONField(help_text="드볼 영역별 과목 리스트(JSON 형태)", null=True, blank=True)

    class Meta:
        unique_together = ('major', 'year')

    def __str__(self):
        return f"{self.major} {self.year}학번 졸업 요건"
