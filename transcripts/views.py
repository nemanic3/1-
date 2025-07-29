from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import Transcript
from .serializers import TranscriptUploadSerializer, TranscriptStatusSerializer, TranscriptParsedSerializer
from users.models import User
from paddleocr import PaddleOCR

# PaddleOCR 초기화 (한국어+영어)
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

class TranscriptUploadView(generics.CreateAPIView):
    serializer_class = TranscriptUploadSerializer
    permission_classes = [permissions.AllowAny]  # 필요 시 IsAuthenticated로 변경

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        # Transcript 객체 생성 (processing 상태)
        transcript = serializer.save(user=user, status='processing')

        # OCR 처리 시도
        try:
            result = ocr.ocr(transcript.file.path)  # OCR 수행
            # 파싱된 결과 → 7개 필드 구조로 변환
            parsed_courses = self.parse_ocr_result(result)

            transcript.parsed_data = {"courses": parsed_courses}
            transcript.status = 'completed'
            transcript.save()

        except Exception:
            transcript.status = 'error'
            transcript.save()

    def parse_ocr_result(self, ocr_result):
        """
        PaddleOCR 결과를 명세서 JSON 구조로 변환
        7개 필드: name, credit, type, major_field, grade, retake, semester
        """
        courses = []
        for line in ocr_result[0]:
            text = line[1][0]
            # TODO: 실제 성적표 구조에 맞게 정교한 파싱 로직 추가
            courses.append({
                "name": text,
                "credit": 3,
                "type": "전공필수",
                "major_field": "전공필수",
                "grade": "A",
                "retake": False,
                "semester": "2025-1"
            })
        return courses


class TranscriptStatusView(generics.RetrieveAPIView):
    serializer_class = TranscriptStatusSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()
        if not transcript:
            return Response({"error": "해당 성적표가 존재하지 않습니다."}, status=404)
        return Response({"status": transcript.status})


class TranscriptParsedView(generics.RetrieveAPIView):
    serializer_class = TranscriptParsedSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        transcript = Transcript.objects.filter(user_id=user_id).last()

        if not transcript:
            return Response({"error": "해당 성적표가 존재하지 않습니다."}, status=404)

        if transcript.status != 'completed':
            return Response({"error": "아직 파싱이 완료되지 않았습니다."}, status=404)

        return Response({"courses": transcript.parsed_data.get("courses", [])})
