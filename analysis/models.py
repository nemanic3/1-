from django.db import models

class GraduationRequirement(models.Model):
    total_required = models.IntegerField(default=132)  # 총 학점
    major_required = models.IntegerField(default=50)   # 전공(필수 포함)
    general_required = models.IntegerField(default=8)  # 교양 필수
    drbol_required = models.IntegerField(default=18)   # 드볼
    special_general_required = models.IntegerField(default=3)  # 특성화 교양
    sw_required = models.IntegerField(default=9)       # SW/데이터활용역량
    msc_required = models.IntegerField(default=23)     # 수리/과학/전산(MSC)

    # 전공 필수 과목 리스트 (콤마 구분)
    major_must_courses = models.TextField(
        help_text="전공 필수 과목명(콤마로 구분)"
    )

    # 드볼 영역 이름 (콤마 구분) - 최소 각 1과목 이상
    drbol_areas = models.TextField(
        help_text="드볼 영역 이름(콤마로 구분)"
    )

    def __str__(self):
        return "Graduation Requirement"
