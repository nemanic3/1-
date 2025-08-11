from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transcripts.models import Transcript
from analysis.models import GraduationRequirement
from users.models import User


def get_valid_courses(transcript):
    """
    F 성적 및 재수강 과목 제외한 유효 과목 리스트 반환
    """
    courses = transcript.parsed_data.get("courses", [])
    return [c for c in courses if c.get("grade") != "F" and not c.get("retake", False)]


def semester_sort_key(sem):
    try:
        year, term = map(int, sem.split('-'))
        return (year, term)
    except:
        return (99, 9)


# ---------- 1. 학기별 전체 이수 현황 ----------
class SemesterCourseListView(APIView):
    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        courses = get_valid_courses(transcript)

        semester_data = {}
        for course in courses:
            sem = course.get("semester", "기타")
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append(course)

        sorted_semesters = sorted(semester_data.keys(), key=semester_sort_key)
        data = {sem: semester_data[sem] for sem in sorted_semesters}
        return Response(data, status=status.HTTP_200_OK)


# ---------- 2. 특정 학기 과목 조회 ----------
class SemesterDetailView(APIView):
    def get(self, request, semester, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        courses = [
            c for c in get_valid_courses(transcript)
            if c.get("semester") == semester
        ]

        return Response({"semester": semester, "courses": courses}, status=status.HTTP_200_OK)


# ---------- 3. 특정 학기의 전공필수 미이수 과목 ----------
class SemesterMissingRequiredView(APIView):
    def get(self, request, semester, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        year_prefix = int(user.student_id[1:3])
        year = 2000 + year_prefix

        requirement = GraduationRequirement.objects.filter(
            major=user.major, year=year
        ).first()

        if not requirement:
            return Response({"error": "졸업 요건 데이터가 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        must_courses_for_semester = [
            c["name"] for c in requirement.major_must_courses
            if c.get("semester") == semester
        ]

        completed_courses = [
            c["name"] for c in get_valid_courses(transcript)
            if c.get("semester") == semester
        ]

        missing_courses = [
            course for course in must_courses_for_semester
            if course not in completed_courses
        ]

        return Response({
            "semester": semester,
            "missing_required_courses": missing_courses
        }, status=status.HTTP_200_OK)


# ---------- 4. 전체 보기 + 필터 ----------
class SemesterFilteredView(APIView):
    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        filter_param = request.GET.get("filter")  # 예: ?filter=전공,교양
        courses = get_valid_courses(transcript)

        if filter_param:
            filter_list = [f.strip() for f in filter_param.split(",")]
            courses = [
                c for c in courses
                if any(f in c.get("type", "") or f in c.get("major_field", "") for f in filter_list)
            ]

        semester_data = {}
        for course in courses:
            sem = course.get("semester", "기타")
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append(course)

        sorted_semesters = sorted(semester_data.keys(), key=semester_sort_key)
        data = {sem: semester_data[sem] for sem in sorted_semesters}
        return Response(data, status=status.HTTP_200_OK)


# ---------- 5. 전체 전공필수 미이수 과목 ----------
class MissingAllRequiredCoursesView(APIView):
    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        year_prefix = int(user.student_id[1:3])
        year = 2000 + year_prefix

        requirement = GraduationRequirement.objects.filter(
            major=user.major, year=year
        ).first()

        if not requirement:
            return Response({"error": "졸업 요건 데이터가 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        all_must_courses = [c["name"] for c in requirement.major_must_courses]
        completed_courses = [c["name"] for c in get_valid_courses(transcript)]

        missing_courses = [c for c in all_must_courses if c not in completed_courses]

        return Response({
            "missing_required_courses": missing_courses
        }, status=status.HTTP_200_OK)

