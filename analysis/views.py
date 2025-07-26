from rest_framework import generics, permissions
from rest_framework.response import Response
from transcripts.models import Transcript
from .models import GraduationRequirement
from .serializers import GraduationStatusSerializer

class GraduationAnalysisView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GraduationStatusSerializer

    def get(self, request, user_id):
        # 최신 성적표 데이터 가져오기
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript or not transcript.parsed_data:
            return Response({"error": "성적표 데이터가 없습니다."}, status=404)

        courses = transcript.parsed_data.get("courses", [])

        # 졸업 요건 불러오기 (첫 번째 행 기준)
        requirement = GraduationRequirement.objects.first()
        if not requirement:
            return Response({"error": "졸업 요건 데이터가 설정되지 않았습니다."}, status=500)

        # -----------------------
        # 1. 영역별 학점 계산
        # -----------------------
        total_credit = sum(c["credit"] for c in courses)
        major_credit = sum(c["credit"] for c in courses if "전공" in c["type"])
        general_credit = sum(c["credit"] for c in courses if "교양필수" in c["type"])
        drbol_credit = sum(c["credit"] for c in courses if "드볼" in c["type"])
        sw_credit = sum(c["credit"] for c in courses if "SW" in c["type"] or "데이터활용" in c["type"])
        msc_credit = sum(c["credit"] for c in courses if "MSC" in c["type"])
        special_general_credit = sum(c["credit"] for c in courses if "특성화교양" in c["type"])

        # -----------------------
        # 2. 전공 필수 과목 체크
        # -----------------------
        must_courses = [c.strip() for c in requirement.major_must_courses.split(",")]
        completed_courses = [c["name"] for c in courses]
        missing_major_courses = [c for c in must_courses if c not in completed_courses]

        # -----------------------
        # 3. 드볼 영역 체크
        # -----------------------
        drbol_areas = [a.strip() for a in requirement.drbol_areas.split(",")]
        completed_areas = {c["type"] for c in courses if "드볼" in c["type"]}
        missing_drbol_areas = [a for a in drbol_areas if a not in completed_areas]

        # -----------------------
        # 4. 졸업 요건 상태 판정
        # -----------------------
        status = "complete"
        msg_list = []

        if total_credit < requirement.total_required:
            status = "pending"
            msg_list.append(f"총 학점 {requirement.total_required - total_credit}학점 부족")
        if major_credit < requirement.major_required:
            status = "pending"
            msg_list.append(f"전공 {requirement.major_required - major_credit}학점 부족")
        if general_credit < requirement.general_required:
            status = "pending"
            msg_list.append(f"교양필수 {requirement.general_required - general_credit}학점 부족")
        if drbol_credit < requirement.drbol_required or missing_drbol_areas:
            status = "pending"
            msg_list.append("드볼 영역 충족 안 됨")
        if sw_credit < requirement.sw_required:
            status = "pending"
            msg_list.append(f"SW/데이터활용 {requirement.sw_required - sw_credit}학점 부족")
        if msc_credit < requirement.msc_required:
            status = "pending"
            msg_list.append(f"MSC {requirement.msc_required - msc_credit}학점 부족")
        if special_general_credit < requirement.special_general_required:
            status = "pending"
            msg_list.append(f"특성화교양 {requirement.special_general_required - special_general_credit}학점 부족")
        if missing_major_courses:
            status = "pending"
            msg_list.append(f"전공 필수 미이수: {', '.join(missing_major_courses)}")

        if not msg_list:
            message = "졸업 요건 충족"
        else:
            message = " / ".join(msg_list)

        # -----------------------
        # 5. 응답 데이터 구성
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

        return Response(data)
