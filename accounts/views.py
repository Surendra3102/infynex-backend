from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterAPIView(APIView):

    def post(self, request):
        data = request.data.copy()

        # Detect role automatically if frontend doesn't send it
        if not data.get("role"):
            if data.get("full_name"):
                data["role"] = "candidate"
            elif data.get("company_name"):
                data["role"] = "employer"

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Registration successful.",
                    "user": {
                        "id": user.id,
                        "role": user.role,
                        "full_name": user.full_name,
                        "current_role": user.current_role,
                        "company_name": user.company_name,
                        "hr_name": user.hr_name,
                        "email": user.email,
                        "phone": user.phone,
                        "website": user.website,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        
        

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "role": user.role,
                        "full_name": user.full_name,
                        "current_role": user.current_role,
                        "company_name": user.company_name,
                        "hr_name": user.hr_name,
                        "email": user.email,
                        "phone": user.phone,
                        "website": user.website,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        
                
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            {
                "success": True,
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .serializers import ForgotPasswordSerializer
from .models import User

token_generator = PasswordResetTokenGenerator()


from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import socket

from .models import User
from .serializers import ForgotPasswordSerializer

token_generator = PasswordResetTokenGenerator()


class ForgotPasswordAPIView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            if user.role == "candidate":
                name = user.full_name
            else:
                name = user.hr_name

        except User.DoesNotExist:
            return Response(
                {
                    "success": True,
                    "message": "If the email exists, a password reset link has been sent.",
                },
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        print("User PK:", user.pk)
        print("UID:", uid)
        print("Token:", token)

        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # ================= DEBUG =================

        print("=" * 60)
        print("EMAIL_HOST:", settings.EMAIL_HOST)
        print("EMAIL_PORT:", settings.EMAIL_PORT)
        print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)
        print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
        print("FRONTEND_URL:", settings.FRONTEND_URL)
        print("RESET LINK:", reset_link)
        print("=" * 60)

        try:
            print("Testing SMTP connection...")

            sock = socket.create_connection(
                (settings.EMAIL_HOST, settings.EMAIL_PORT),
                timeout=10,
            )

            print("✅ SMTP connection successful")
            sock.close()

        except Exception as e:
            print("❌ SMTP connection failed:", repr(e))

        # ================= END DEBUG =================

        send_mail(
            subject="Reset Your Password",
            message=f"""
Hello {name},

We received a request to reset your password.

Click the link below to reset it:

{reset_link}

If you did not request this, you can safely ignore this email.

Thanks,
Infynex HR Portal
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {
                "success": True,
                "message": "Password reset link sent successfully.",
            },
            status=status.HTTP_200_OK,
        )
         
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from .serializers import ResetPasswordSerializer


class ResetPasswordAPIView(APIView):

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {
                    "success": False,
                    "message": "Invalid reset link.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token_generator.check_token(user, token):
            return Response(
                {
                    "success": False,
                    "message": "Reset link has expired or is invalid.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {
                "success": True,
                "message": "Password has been reset successfully.",
            },
            status=status.HTTP_200_OK,
        )