from rest_framework import serializers
from .models import User


import re
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "role",
            "full_name",
            "current_role",
            "company_name",
            "hr_name",
            "email",
            "phone",
            "website",
            "password",
        ]

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_full_name(self, value):
        if value:
            value = value.strip()

            if len(value) < 3:
                raise serializers.ValidationError(
                    "Name must be at least 3 characters."
                )

            if not re.match(r"^[A-Za-z ]+$", value):
                raise serializers.ValidationError(
                    "Name can contain only letters and spaces."
                )

        return value

    def validate_hr_name(self, value):
        if value:
            value = value.strip()

            if len(value) < 3:
                raise serializers.ValidationError(
                    "Name must be at least 3 characters."
                )

            if not re.match(r"^[A-Za-z ]+$", value):
                raise serializers.ValidationError(
                    "Name can contain only letters and spaces."
                )

        return value

    def validate_phone(self, value):
        if value:
            if not re.match(r"^[6-9]\d{9}$", value):
                raise serializers.ValidationError(
                    "Enter a valid 10-digit mobile number."
                )

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters."
            )

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r"[@$!%*?&]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def validate(self, attrs):
        role = attrs.get("role")

        if role == "candidate":

            if not attrs.get("full_name"):
                raise serializers.ValidationError({
                    "full_name": "Full name is required."
                })

            if not attrs.get("phone"):
                raise serializers.ValidationError({
                    "phone": "Phone number is required."
                })

        elif role == "employer":

            if not attrs.get("company_name"):
                raise serializers.ValidationError({
                    "company_name": "Company name is required."
                })

            if not attrs.get("hr_name"):
                raise serializers.ValidationError({
                    "hr_name": "HR name is required."
                })

        else:
            raise serializers.ValidationError({
                "role": "Invalid role."
            })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user
    


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role")

        user = authenticate(
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError({
                "email": "Invalid email or password."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "email": "Your account has been deactivated."
            })

        # Candidate / Employer validation
        if role and user.role != role:
            raise serializers.ValidationError({
                "role": "Please select the correct account type."
            })

        attrs["user"] = user
        return attrs
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "role",
            "full_name",
            "current_role",
            "company_name",
            "hr_name",
            "email",
            "phone",
            "website",
        ]



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value
    
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs