from rest_framework import generics, permissions
from rest_framework.response import Response
from transcripts.models import Transcript
from users.models import User
from .models import GraduationRequirement
from .serializers import GraduationStatusSerializer


# ---------------------------
# 공통 로직 (계산용 함수)
# ---------------------------
def analyze_graduation(user_id):
    """
    졸업 요건 분석을 위한 공통 계산 로직
    """
    # 1. 유저 확인
    user = User.objects.filter(id=user_id).first()
    if not user:
        return {"error": "사용자를 찾을 수 없습니다.", "status": 404}

    # 2. 성적표 확인
    transcript = Transcript.objects.filter(user_id=user_id).last()
    if not transcript or not transcript.parsed_data:
        return {"error": "성적표 데이터가 없습니다.", "status": 404}

    courses = transcript.parsed_data.get("courses", [])

    # 3. 졸업 요건 확인 (학번/학과)
    year_prefix = int(user.student_id[1:3])  # 예: C25XXXX → 25
    year = 2000 + year_prefix
    requirement = GraduationRequirement.objects.filter(
        major=user.major, year=year
    ).first()
    if not requirement:
        return {"error": "졸업 요건 데이터가 없습니다.", "status": 500}

    # -----------------------
    # 학점 및 필수 과목 계산
    # -----------------------
    # F 과목 및 재수강 과목 제외
    valid_courses = [
        c for c in courses
        if c.get("grade") != "F" and not c.get("retake", False)
    ]

    total_credit = sum(c["credit"] for c in valid_courses)
    major_credit = sum(c["credit"] for c in valid_courses if "전공" in c["type"])
    general_credit = sum(c["credit"] for c in valid_courses if "교양" in c["type"])
    drbol_credit = sum(c["credit"] for c in valid_courses if "드볼" in c["type"])
    sw_credit    = sum(c["credit"] for c in valid_courses if "SW" in c["type"] or "데이터활용" in c["type"])
    msc_credit   = sum(c["credit"] for c in valid_courses if "MSC" in c["type"])
    special_general_credit = sum(c["credit"] for c in valid_courses if "특성화교양" in c["type"])

    # 전공 필수 과목 체크 (JSONField 리스트에서 name만 추출)
    must_courses = [ item.get("name") for item in requirement.major_must_courses ]
    completed_major_must = [
        c["name"] for c in valid_courses
        if c.get("major_field") == "전공필수"
    ]
    missing_major_courses = [
        course for course in must_courses
        if course not in completed_major_must
    ]

    # 드볼 영역 체크
    drbol_areas = [ a.strip() for a in requirement.drbol_areas.split(",") ]
    completed_areas = { c["major_field"] for c in valid_courses if c.get("major_field") in drbol_areas }
    missing_drbol_areas = [ area for area in drbol_areas if area not in completed_areas ]

    # -----------------------
    # 졸업 요건 상태 판정
    # -----------------------
    status = "complete"
    messages = []

    if total_credit < requirement.total_required:
        status = "pending"
        messages.append(f"총 학점 {requirement.total_required - total_credit}학점 부족")
    if major_credit < requirement.major_required:
        status = "pending"
        messages.append(f"전공 {requirement.major_required - major_credit}학점 부족")
    if general_credit < requirement.general_required:
        status = "pending"
        messages.append(f"교양필수 {requirement.general_required - general_credit}학점 부족")
    if drbol_credit < requirement.drbol_required or missing_drbol_areas:
        status = "pending"
        messages.append("드볼 영역 충족 안 됨")
    if sw_credit < requirement.sw_required:
        status = "pending"
        messages.append(f"SW/데이터활용 {requirement.sw_required - sw_credit}학점 부족")
    if msc_credit < requirement.msc_required:
        status = "pending"
        messages.append(f"MSC {requirement.msc_required - msc_credit}학점 부족")
    if special_general_credit < requirement.special_general_required:
        status = "pending"
        messages.append(f"특성화교양 {requirement.special_general_required - special_general_credit}학점 부족")
    if missing_major_courses:
        status = "pending"
        messages.append(f"전공 필수 미이수: {', '.join(missing_major_courses)}")

    message = " / ".join(messages) if messages else "졸업 요건 충족"

    # -----------------------
    # 최종 응답 데이터 구성
    # -----------------------
    data = {
        "total_completed": total_credit,
        "total_required": requirement.total_required,
        "major_completed": major_credit,
        "major_required": requirement.major_required,
        "general_completed": general_credit,
        "general_required": requirement.general_required,
        "drbol_completed": drbol_credit,
        "drbol_required": requirement.drbol_required,
        "sw_completed": sw_credit,
        "sw_required": requirement.sw_required,
        "msc_completed": msc_credit,
        "msc_required": requirement.msc_required,
        "special_general_completed": special_general_credit,
        "special_general_required": requirement.special_general_required,
        "missing_major_courses": missing_major_courses,
        "missing_drbol_areas": missing_drbol_areas,
        "graduation_status": status,
        "message": message
    }

    return {"data": data, "status": 200}



# ---------------------------
# View 클래스들
# ---------------------------
class GeneralCoursesView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        data = result["data"]
        return Response({
            "필수교양": ["논리적사고와글쓰기", "전공기초영어(1)"],  # TODO: 실제 교양필수 과목명 DB에서 불러오기
            "이수여부": data["general_completed"] >= data["general_required"]
        })


class MajorCoursesView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        data = result["data"]
        return Response({
            "전공필수": data["missing_major_courses"],
            "전공선택": []  # TODO: 필요 시 추가 로직
        })


class TotalCreditView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        return Response({"total_credit": result["data"]["total_completed"]})


class GeneralCreditView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        return Response({"general_credit": result["data"]["general_completed"]})


class MajorCreditView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        return Response({"major_credit": result["data"]["major_completed"]})


class StatisticsCreditView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        data = result["data"]
        general_rate = data["general_completed"] / data["general_required"] if data["general_required"] else 0
        major_rate = data["major_completed"] / data["major_required"] if data["major_required"] else 0

        return Response({"general_rate": general_rate, "major_rate": major_rate})


class StatusCreditView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GraduationStatusSerializer

    def get(self, request, user_id):
        result = analyze_graduation(user_id)
        if "error" in result:
            return Response({"error": result["error"]}, status=result["status"])

        return Response(result["data"])
