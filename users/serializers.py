from rest_framework import serializers
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    student_id = serializers.RegexField(
        regex=r'^[A-Za-z]\d{6}$',
        max_length=7,
        error_messages={'invalid': '학번은 영문자 1자 + 숫자 6자리여야 합니다.'}
    )
    full_name = serializers.RegexField(
        regex=r'^[가-힣]{2,5}$',
        max_length=5,
        error_messages={'invalid': '이름은 한글 2~5자만 입력 가능합니다.'}
    )

    class Meta:
        model = User
        # 전공(major) 포함
        fields = ['student_id', 'full_name', 'current_year', 'major']

    def validate_student_id(self, value):
        # API 레벨에서 대문자로 정규화
        return value.upper()

    def create(self, validated_data):
        # major 포함해서 User 생성
        user = User(
            student_id=validated_data['student_id'],
            full_name=validated_data['full_name'],
            current_year=validated_data['current_year'],
            major=validated_data['major'],
            username=validated_data['student_id'],  # AbstractUser 때문에 username 필드 채움
        )
        user.set_unusable_password()  # 비밀번호 사용 안 함
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # major 포함해서 조회용에도 표시
        fields = ['student_id', 'full_name', 'current_year', 'major']
        read_only_fields = ['student_id']  # student_id는 수정 불가
