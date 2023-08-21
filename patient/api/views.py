from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PatientSerializer
from patient.models import Patient
from .authentication import PatientAuthentication
from lab.models import Bills
from lab.api.serializers import BillSerializer
from lab.api.helper import get_bill_context, generate_pdf_response, test_mapping, make_test_context


class PatientAPIVIew(APIView):

    def get(self, request, pk):
        try:
            patients = User.objects.get(id=pk)
        except User.DoesNotExist as _:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)

        serializer = PatientSerializer(patients)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = get_object_or_404(User, username=data.get('username'))
                password_hash = make_password(data.get('password'))

                user.first_name = data.get("first_name")
                user.password = password_hash
                user.email = data.get("email")
                user.save()

            except Http404 as _:
                user_payload = {
                    "username": data.get('username'),
                    "password": data.get('password'),
                    "first_name": data.get('first_name'),
                    "email": data.get('email'),
                }
                user = User.objects.create_user(**user_payload)
            Patient.objects.create(user=user)
            new_serializer = PatientSerializer(user)
            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillsAPIView(APIView):
    authentication_classes = [PatientAuthentication]

    def get(self, request):
        patient = request.patient
        bills = Bills.objects.filter(patient=patient.id)
        if bills:
            for bill in bills:
                bill.tests = bill.tests_set.all()

        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)


class PrintBillAPIView(APIView):
    authentication_classes = [PatientAuthentication]

    def get(self, request):
        try:
            bill_id = request.GET.get('bill_id')
            bill = Bills.objects.get(id=bill_id, patient=request.patient.id)
        except Bills.DoesNotExist as _:
            return Response({'error': 'Bill with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        context = get_bill_context(bill)
        response = generate_pdf_response(template='bill.html', context=context)
        return response


class ReportAPIView(APIView):
    authentication_classes = [PatientAuthentication]

    def get(self, request):
        try:
            bill_id = request.GET.get('bill_id')
            bill = Bills.objects.get(id=bill_id, patient=request.patient.id)
        except Bills.DoesNotExist as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tests = bill.tests_set.all()
        if any(test.tests_status == 'pending' for test in tests):
            return Response({'error': 'tests are not completed'}, status=status.HTTP_403_FORBIDDEN)

        if bill.payment_status != 'paid':
            return Response({'error': 'please, first pay your bill'}, status=status.HTTP_400_BAD_REQUEST)

        tests_params = []
        for test in tests:
            parameter_class = test_mapping.get(test.name)
            try:
                test_params_obj = parameter_class.objects.get(test=test.id)
            except parameter_class.DoesNotExist:
                return Response({'error': 'test not found'}, status=status.HTTP_400_BAD_REQUEST)

            test_params_obj.test_name = test.name
            tests_params.append(test_params_obj)

        test_context = make_test_context(tests_params, patient=bill.patient)
        response = generate_pdf_response(template='report.html', context=test_context)
        return response
