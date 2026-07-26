from rest_framework import serializers


class ContactSerializer(serializers.Serializer):
    CONTACT_TYPES = (
        ("hiring", "I'm Hiring"),
        ("seeker", "Job Seeker"),
        ("general", "General Inquiry"),
    )

    type = serializers.ChoiceField(
        choices=CONTACT_TYPES,
        error_messages={
            "required": "Contact type is required.",
            "invalid_choice": "Invalid contact type.",
        },
    )

    name = serializers.CharField(
        max_length=100,
        error_messages={
            "required": "Full name is required.",
            "blank": "Full name cannot be blank.",
        },
    )

    email = serializers.EmailField(
        error_messages={
            "required": "Email address is required.",
            "invalid": "Enter a valid email address.",
        },
    )

    phone = serializers.CharField(
        max_length=15,
        error_messages={
            "required": "Phone number is required.",
            "blank": "Phone number cannot be blank.",
        },
    )

    company = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
    )

    subject = serializers.CharField(
        max_length=200,
        error_messages={
            "required": "Subject is required.",
            "blank": "Subject cannot be blank.",
        },
    )

    message = serializers.CharField(
        error_messages={
            "required": "Message is required.",
            "blank": "Message cannot be blank.",
        },
    )
    
from rest_framework import serializers


class EmployerRequestSerializer(serializers.Serializer):
    company = serializers.CharField(max_length=255)
    contactPerson = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    hiringType = serializers.CharField(max_length=100)
    positions = serializers.IntegerField(min_value=1)
    timeline = serializers.CharField(max_length=100)
    message = serializers.CharField(
        required=False,
        allow_blank=True
    )