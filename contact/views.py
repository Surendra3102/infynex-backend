from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactSerializer


class ContactAPIView(APIView):

    def post(self, request):
        serializer = ContactSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        contact_type = dict(ContactSerializer.CONTACT_TYPES).get(
            data["type"], data["type"]
        )

        subject = f"New Contact Enquiry - {contact_type}"

        message = f"""
New Contact Enquiry

Contact Type : {contact_type}

Full Name    : {data['name']}
Email        : {data['email']}
Phone        : {data['phone']}
Company      : {data.get('company', 'N/A')}

Subject      : {data['subject']}

Message:
{data['message']}
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.COMPANY_EMAIL],
            fail_silently=False,
        )

        return Response(
            {
                "success": True,
                "message": "Your enquiry has been sent successfully.",
            },
            status=status.HTTP_200_OK,
        )
        
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import EmployerRequestSerializer


class EmployerRequestAPIView(APIView):

    def post(self, request):

        serializer = EmployerRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        send_mail(
            subject=f"New Hiring Request - {data['company']}",
            message=f"""
A new hiring request has been submitted.

====================================

Company Name:
{data['company']}

Contact Person:
{data['contactPerson']}

Business Email:
{data['email']}

Phone Number:
{data['phone']}

Hiring Requirement:
{data['hiringType']}

Number of Positions:
{data['positions']}

Hiring Timeline:
{data['timeline']}

Additional Details:
{data['message']}

====================================

Infynex HR Portal
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                settings.DEFAULT_FROM_EMAIL
            ],
            fail_silently=False,
        )

        return Response(
            {
                "success": True,
                "message":
                "Your hiring request has been submitted successfully. Our recruitment team will contact you shortly."
            },
            status=status.HTTP_200_OK,
        )