from rest_framework import serializers
from .models import Transcript

# 업로드 전용
class TranscriptUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['file']

# 상태 조회 전용
class TranscriptStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['status']

# 파싱 데이터 조회 전용
class TranscriptParsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['parsed_data']
