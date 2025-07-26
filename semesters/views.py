from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transcripts.models import Transcript
from analysis.models import GraduationRequirement


# ---------- 1. 학기별 전체 이수 현황 ----------
class SemesterCourseListView(APIView):
    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        courses = transcript.parsed_data.get("courses", [])

        # 학기별 그룹화
        semester_data = {}
        for course in courses:
            sem = course.get("semester", "기타")
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append(course)

        # 학기 정렬 (1-1, 1-2, 2-1, 2-2 ...)
        sorted_semesters = sorted(semester_data.keys(), key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1])))

        data = {sem: semester_data[sem] for sem in sorted_semesters}

        return Response(data, status=status.HTTP_200_OK)


# ---------- 2. 특정 학기 과목 조회 ----------
class SemesterDetailView(APIView):
    def get(self, request, semester, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        courses = [c for c in transcript.parsed_data.get("courses", []) if c.get("semester") == semester]

        return Response({"semester": semester, "courses": courses}, status=status.HTTP_200_OK)


# ---------- 3. 특정 학기 미이수 과목 ----------
class SemesterMissingRequiredView(APIView):
    def get(self, request, semester, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        requirement = GraduationRequirement.objects.first()
        if not requirement:
            return Response({"error": "졸업 요건 데이터가 없습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        must_courses = [c.strip() for c in requirement.major_must_courses.split(",")]
        completed_courses = [
            c["name"] for c in transcript.parsed_data.get("courses", [])
            if c.get("semester") == semester
        ]

        missing_courses = [course for course in must_courses if course not in completed_courses]

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

        filter_param = request.GET.get("filter")  # ex) 전공,교양
        courses = transcript.parsed_data.get("courses", [])

        # 필터 처리
        if filter_param:
            filter_list = [f.strip() for f in filter_param.split(",")]
            courses = [c for c in courses if any(f in c.get("type", "") for f in filter_list)]

        # 학기별 그룹화
        semester_data = {}
        for course in courses:
            sem = course.get("semester", "기타")
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append(course)

        sorted_semesters = sorted(semester_data.keys(), key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1])))

        data = {sem: semester_data[sem] for sem in sorted_semesters}

        return Response(data, status=status.HTTP_200_OK)
