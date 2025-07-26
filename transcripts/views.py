from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Transcript
from .serializers import TranscriptUploadSerializer, TranscriptStatusSerializer, TranscriptParsedSerializer
from users.models import User
from paddleocr import PaddleOCR

# PaddleOCR 초기화 (한국어+영어)
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

# 파일 업로드
class TranscriptUploadView(generics.CreateAPIView):
    serializer_class = TranscriptUploadSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        # Transcript 객체 생성 (processing 상태)
        transcript = serializer.save(user=user, status='processing')

        # OCR 처리 시도
        try:
            result = ocr.ocr(transcript.file.path)  # OCR 수행
            # 파싱된 결과 → 명세서 형식으로 가공
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
        (여기서는 예시: 이름/학점/학기/이수구분 단순 매핑)
        """
        courses = []
        for line in ocr_result[0]:
            text = line[1][0]
            # TODO: 실제 성적표 구조에 맞게 파싱 로직 추가
            courses.append({
                "name": text,
                "credit": 3,
                "semester": "2025-1",
                "type": "전공필수"
            })
        return courses

# 상태 조회
class TranscriptStatusView(generics.RetrieveAPIView):
    serializer_class = TranscriptStatusSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return Transcript.objects.filter(user_id=user_id).last()

# 파싱된 데이터 조회
class TranscriptParsedView(generics.RetrieveAPIView):
    serializer_class = TranscriptParsedSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        transcript = Transcript.objects.filter(user_id=user_id).last()

        # 상태가 완료되지 않았다면 오류 응답
        if transcript and transcript.status != 'completed':
            self.serializer_class.Meta.fields = ['parsed_data']
            raise serializers.ValidationError({"error": "아직 파싱이 완료되지 않았습니다."})

        return transcript
