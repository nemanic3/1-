# transcripts/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import Transcript
from .serializers import (
    TranscriptUploadSerializer,
    TranscriptStatusSerializer,
    TranscriptParsedSerializer
)



def _rows_to_tsv(rows: list[list[str]]) -> str:
    return "\n".join("\t".join(map(str, r)) for r in rows)


class TranscriptUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, user_id):
        if request.user.id != user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # ✅ 여기서만 import (지연 임포트)
        try:
            from .tasks import process_transcript
        except Exception as e:
            return Response({"error": f"OCR 모듈 로드 실패: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'files' not in request.data:
            return Response({"error": "파일이 전송되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TranscriptUploadSerializer(
            data={"files": request.data.getlist('files')},
            context={'request': request}
        )
        if serializer.is_valid():
            transcript = serializer.save()
            # Celery 비동기 실행
            process_transcript.delay(transcript.id)
            return Response({"message": "업로드 완료", "status": "processing"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TranscriptStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        # 1) 인증 체크
        if request.user.id != user_id:
            return Response(
                {"error": "인증이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2) 최신 업로드 한 건만 조회
        transcript = (
            Transcript.objects
            .filter(user_id=user_id)
            .order_by('-created_at')
            .first()
        )
        if not transcript:
            return Response(
                {"error": "해당 성적표가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3) 상태 반환 (소문자)
        return Response(
            {"status": transcript.status.lower()},
            status=status.HTTP_200_OK
        )


class TranscriptParsedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"error": "인증이 필요합니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        transcript = Transcript.objects.filter(user_id=user_id).order_by('-created_at').first()

        if not transcript:
            return Response(
                {"error": "해당 성적표가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 상태가 'done'이 아니거나, 'done'인데 데이터가 없는 경우
        if transcript.status.lower() != 'done' or not transcript.parsed_data:
            return Response(
                {"error": "아직 파싱이 완료되지 않았거나 결과가 없습니다."},
                status=status.HTTP_404_NOT_FOUND  # 명세에 따라 404 유지
            )

        # 파싱된 JSON 데이터를 그대로 반환
        # 파싱된 JSON 데이터를 그대로 반환  ← 이 부분을 전부 교체
        data = transcript.parsed_data

        # 새 파이프라인: 2차원 rows로 저장된 경우 → 학기별 블록 텍스트로 반환
        if isinstance(data, list) and data and isinstance(data[0], list):
            return HttpResponse(rows_to_text(data, group_by_term=True),
                                content_type="text/plain; charset=utf-8")

        # 이미 문자열이면 그대로 반환
        if isinstance(data, str):
            return HttpResponse(data, content_type="text/plain; charset=utf-8")

        # 그 외(예: 과거 포맷 등)는 JSON 그대로 반환
        return Response(data, status=status.HTTP_200_OK)
        # ----- 교체 끝 -----