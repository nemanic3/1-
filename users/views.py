from rest_framework import generics, permissions
from .models import User
from .serializers import SignupSerializer, UserSerializer

# 회원가입
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

# 내 정보 조회 (쿼리 파라미터 기반)
class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def get_object(self):
        student_id = self.request.query_params.get('student_id')
        full_name = self.request.query_params.get('full_name')
        entry_year = self.request.query_params.get('entry_year')
        return User.objects.filter(
            student_id=student_id,
            full_name=full_name,
            entry_year=entry_year
        ).first()

# 내 정보 수정 (쿼리 파라미터 기반)
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def get_object(self):
        student_id = self.request.query_params.get('student_id')
        full_name = self.request.query_params.get('full_name')
        entry_year = self.request.query_params.get('entry_year')
        return User.objects.filter(
            student_id=student_id,
            full_name=full_name,
            entry_year=entry_year
        ).first()
