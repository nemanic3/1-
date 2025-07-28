from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import SignupSerializer, UserSerializer

# 회원가입(student_id, full_name)
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

# JWT 로그인 (access/refresh 토큰 발급)
class LoginView(TokenObtainPairView):
    # 기본 TokenObtainPairSerializer를 사용
    pass

# JWT refresh (optional)
# from rest_framework_simplejwt.views import TokenRefreshView

# 로그아웃: refresh token을 블랙리스트 처리
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh 토큰을 함께 보내주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response(
                {'detail': '유효하지 않은 토큰입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)

# 내 정보 조회
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

class MeView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]  # 로그인 없이 접근
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student_id')  # /me/?student_id=C555555

        if not student_id:
            raise NotFound("student_id 쿼리 파라미터를 제공해야 합니다.")

        try:
            user = User.objects.get(student_id=student_id.upper())
        except User.DoesNotExist:
            raise NotFound("해당 학번의 사용자를 찾을 수 없습니다.")

        serializer = self.get_serializer(user)
        return Response(serializer.data)


# 내 정보 수정 (full_name, current_year 등)
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [AllowAny]  # 로그인 없이 접근
    serializer_class = UserSerializer

    def get_object(self):
        # 쿼리 파라미터에서 student_id 가져오기
        student_id = self.request.query_params.get('student_id')
        if not student_id:
            raise NotFound("student_id 쿼리 파라미터를 제공해야 합니다.")

        try:
            return User.objects.get(student_id=student_id.upper())
        except User.DoesNotExist:
            raise NotFound("해당 학번의 사용자를 찾을 수 없습니다.")

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        # 수정 허용 필드만 체크
        allowed_fields = {'full_name', 'major'}
        if any(field not in allowed_fields for field in request.data.keys()):
            return Response(
                {"error": "수정할 수 없는 필드가 포함되어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 데이터 업데이트
        for field, value in request.data.items():
            setattr(user, field, value)
        user.save()

        return Response({"message": "정보 수정 완료"}, status=status.HTTP_200_OK)