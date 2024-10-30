from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from accounts.models import CustomUser
from ..serializers.account_serializers import UserSerializer, UserRegistrationSerializer
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'is_teacher': getattr(user, 'is_teacher', False),
                'is_student': getattr(user, 'is_student', False)
            })
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Safely handle token deletion
        if hasattr(request, 'auth') and request.auth:
            request.auth.delete()
        return Response(status=status.HTTP_200_OK)

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(id=user_id)
            
            if user.email_verified:
                return Response(
                    {'message': 'Email already verified'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.otp == otp:
                if user.otp_created_at + timedelta(minutes=10) >= timezone.now():
                    user.email_verified = True
                    user.save()
                    
                    # Create token for authenticated user
                    token, _ = Token.objects.get_or_create(user=user)
                    
                    return Response({
                        'message': 'Email verified successfully',
                        'token': token.key,
                        'user_id': user.id,
                        'username': user.username,
                        'is_teacher': user.is_teacher,
                        'is_student': user.is_student
                    })
                else:
                    return Response(
                        {'error': 'OTP expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'error': 'Invalid OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
