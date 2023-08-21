from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .helper import make_test_context, generate_pdf_response, test_mapping, test_serializer_mapping, get_bill_payload, \
    get_bill_context
from .permissions import LabPermission
from .serializers import LabSerializer, LabUserSerializer, BaseUserSerializer, PatientSerializer, BillSerializer
from .authentication import LabAuthentication
from lab.models import Lab, LabUser, LabPatient, Bills, Tests

from patient.models import Patient


class LabAPIView(APIView):

    def post(self, request):
        serializer = LabSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            lab_payload = {
                "name": data.get('name'),
                "address": data.get('address'),
                "pincode": data.get("pincode"),
                "email": data.get("user").get("email"),
            }
            lab = Lab.objects.create(**lab_payload)
            user = User.objects.create_user(**data.get("user"))
            LabUser.objects.create(is_admin=True, lab=lab, user=user)
            serializer = LabSerializer(lab)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberAPIView(APIView):
    authentication_classes = [LabAuthentication]
    permission_classes = [LabPermission]

    def get(self, request):
        user_id = request.GET.get('labUserId')
        if user_id:
            try:
                user = LabUser.objects.get(id=user_id, user__is_active=True)
            except LabUser.DoesNotExist as _:
                return Response("User does not exists", status=status.HTTP_400_BAD_REQUEST)
            serializer = LabUserSerializer(user)
        else:
            users = LabUser.objects.filter(lab=request.user.lab_user.lab, user__is_active=True)
            serializer = LabUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BaseUserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            lab_user = LabUser.objects.create(lab=request.user.lab_user.lab, user=user)
            labuser_serializer = LabUserSerializer(lab_user)
            return Response(labuser_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            pk = request.GET.get('labUserId')
            lab_user = LabUser.objects.get(id=pk, lab=request.user.lab_user.lab)
            user = lab_user.user
        except LabUser.DoesNotExist as _:
            return Response('User does not found', status=status.HTTP_400_BAD_REQUEST)

        serializer = BaseUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if password := serializer.validated_data.pop('password', None):
                password_hash = make_password(password)
                serializer.validated_data['password'] = password_hash
            serializer.save()
            new_serializer = LabUserSerializer(lab_user)
            return Response(new_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            pk = request.GET.get('labUserId')
            lab_user = LabUser.objects.get(id=pk, lab=request.user.lab_user.lab)
            user = lab_user.user
        except LabUser.DoesNotExist as _:
            return Response({'error': 'User does not found'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()

        return Response('User deleted', status=status.HTTP_204_NO_CONTENT)


class PatientAPIView(APIView):
    authentication_classes = [LabAuthentication]
    permission_classes = [LabPermission]

    def get(self, request):
        patient_id = request.GET.get('labPatientId')
        if patient_id:
            try:
                patient = LabPatient.objects.get(id=patient_id, lab=request.user.lab_user.lab)
            except LabPatient.DoesNotExist as _:
                return Response("Patient does not exists", status=status.HTTP_400_BAD_REQUEST)
            serializer = PatientSerializer(patient)
        else:
            patients = LabPatient.objects.filter(lab=request.user.lab_user.lab)
            serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            lab = request.user.lab_user.lab
            data = serializer.validated_data
            try:
                user = get_object_or_404(User, username=data.get('contact'))
            except Http404 as _:
                patient_payload = {
                    "username": data.get('contact'),
                    "first_name": data.get('first_name'),
                    "email": data.get('email'),
                }
                user = User.objects.create_user(**patient_payload)
            lab_patient = LabPatient.objects.create(**data, lab=lab, lab_user=request.user.lab_user, user=user)
            Patient.objects.create(user=user)

            serializer = PatientSerializer(lab_patient)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            pk = request.GET.get('labPatientId')
            lab_patient = LabPatient.objects.get(id=pk, lab=request.user.lab_user.lab)
        except LabPatient.DoesNotExist as _:
            return Response({'error': 'User does not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PatientSerializer(lab_patient, data=request.data, partial=True)
        if serializer.is_valid():
            data = serializer.validated_data
            if contact := data.get('contact'):
                try:
                    user = get_object_or_404(User, username=contact)
                except Http404 as _:
                    user_paylaod = {
                        "first_name": data.get('first_name', lab_patient.first_name),
                        "username": data.get('contact'),
                        "email": data.get('email', lab_patient.email),
                    }
                    user = User.objects.create_user(**user_paylaod)

                serializer.validated_data['user'] = user
            serializer = PatientSerializer(serializer.save())
            return Response(serializer.data)

        return Response(serializer.errors)

    def delete(self, request):
        try:
            pk = request.GET.get('labPatientId')
            patient = LabPatient.objects.get(id=pk, lab=request.user.lab_user.lab)
        except LabPatient.DoesNotExist as _:
            return Response({'message': 'User does not found'}, status=status.HTTP_400_BAD_REQUEST)

        patient.delete()

        return Response({'message': 'Patient deleted'}, status=status.HTTP_204_NO_CONTENT)


class BillPrintAPIView(APIView):
    authentication_classes = [LabAuthentication]
    permission_classes = [LabPermission]

    def get(self, request):
        try:
            pk = request.GET.get('billId')
            bill = Bills.objects.get(id=pk)
            lab_patient = LabPatient.objects.get(user=bill.patient)
            bill.lab_patient = lab_patient
        except Bills.DoesNotExist as _:
            return Response({'error': 'Bill with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        context = get_bill_context(bill)
        return generate_pdf_response(template='bill.html', context=context)


class BillAPIView(APIView):
    authentication_classes = [LabAuthentication]
    permission_classes = [LabPermission]

    def get(self, request):
        pk = request.GET.get('billId')
        if pk:
            try:
                bill = Bills.objects.get(id=pk)
                bill.tests = bill.tests_set.all()
                serializer = BillSerializer(bill)
                return Response(serializer.data)
            except Bills.DoesNotExist as _:
                return Response({'error': 'Bill with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            bills = Bills.objects.filter(lab=request.user.labuser.lab)
            for bill in bills:
                bill.tests = bill.tests_set.all()
            serializer = BillSerializer(bills, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            try:
                pk = request.GET.get('labPatientId')
                lab_patient = LabPatient.objects.get(id=pk, lab=request.user.labuser.lab)
            except LabPatient.DoesNotExist as _:
                return Response({'message': 'Patient does not found'}, status=status.HTTP_400_BAD_REQUEST)

            patient = lab_patient.user
            data = serializer.validated_data

            bill_payload = get_bill_payload(request, data, patient)
            bill = Bills.objects.create(**bill_payload)

            test_objs = []
            for test in data['tests']:
                obj = Tests.objects.create(**test, bill=bill, lab=request.user.labuser.lab, patient=patient)
                test_objs.append(obj)

            bill.tests = test_objs
            serializer = BillSerializer(bill)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors)

    def put(self, request):
        try:
            pk = request.GET.get('billId')
            bill = Bills.objects.get(id=pk, lab=request.user.lab_user.lab)
        except Bills.DoesNotExist as _:
            return Response({'error': 'Bill with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            bill.tests = bill.tests_set.all()
            serializer = BillSerializer(bill, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'bill updated'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FillTestAPIView(APIView):
    authentication_classes = [LabAuthentication]
    permission_classes = [LabPermission]

    def post(self, request):

        try:
            test_id = request.GET.get('test_id')
            test = Tests.objects.get(id=test_id, lab=request.labuser.lab)
        except Tests.DoesNotExist as _:
            return Response({'error': 'Invalid test id'}, status=status.HTTP_400_BAD_REQUEST)

        test_parameter_class = test_mapping.get(test.name)
        serializer_class = test_serializer_mapping.get(test.name)

        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            test_parameter_class.objects.create(**serializer.validated_data, test=test)
            test.tests_status = 'competed'
            test.save()
            return Response({'message': 'tests data uploaded'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportAPIView(APIView):

    def get(self, request):
        try:
            bill_id = request.GET.get('bill_id')
            bill = Bills.objects.get(id=bill_id, lab=request.labuser.lab)
        except Bills.DoesNotExist as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tests = bill.tests_set.all()
        if any(test.tests_status == 'pending' for test in tests):
            return Response({'error': 'tests are not completed'}, status=status.HTTP_403_FORBIDDEN)

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
