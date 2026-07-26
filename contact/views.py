from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail


from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from .serializers import ContactSerializer, EmployerRequestSerializer
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
            data["type"],
            data["type"],
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

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        email = sib_api_v3_sdk.SendSmtpEmail(
            sender={
                "name": "Infynex HR Portal",
                "email": settings.DEFAULT_FROM_EMAIL,
            },
            to=[
                {
                    "email": settings.COMPANY_EMAIL,
                    "name": "Infynex",
                }
            ],
            subject=subject,
            text_content=message,
        )

        try:
            api_instance.send_transac_email(email)

        except ApiException as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

        serializer = EmployerRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        message = f"""
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
"""

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        email = sib_api_v3_sdk.SendSmtpEmail(
            sender={
                "name": "Infynex HR Portal",
                "email": settings.DEFAULT_FROM_EMAIL,
            },
            to=[
                {
                    "email": settings.COMPANY_EMAIL,
                    "name": "Infynex",
                }
            ],
            subject=f"New Hiring Request - {data['company']}",
            text_content=message,
        )

        try:
            api_instance.send_transac_email(email)

        except ApiException as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "success": True,
                "message": "Your hiring request has been submitted successfully. Our recruitment team will contact you shortly.",
            },
            status=status.HTTP_200_OK,
        )