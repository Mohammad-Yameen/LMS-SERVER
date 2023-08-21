from rest_framework import serializers

from django.contrib.auth.models import User

from lab.models import Lab, LabUser, LabPatient, LiverFunctionTest, CholesterolProfileTest, UrinalysisTest, CBCTest, \
    Bills, Tests


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name']
        extra_kwargs = {'password': {'write_only': True}}


class LabUserSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer()

    class Meta:
        model = LabUser
        fields = ['id', 'user', 'lab', 'is_admin']
        read_only_fields = ['lab', 'is_admin']


class LabSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(write_only=True)

    class Meta:
        model = Lab
        fields = ['id', 'name', 'address', 'pincode', 'user']
        extra_kwargs = {'lab_user': {'write_only': True}}
        read_only_fields = ['email', 'contact']


class PatientSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = LabPatient
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'lab_user', 'lab']

    def to_representation(self, instance):
        return super().to_representation(instance)


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tests
        fields = ['id', 'name', 'price']
        read_only_fields = ['bill', 'lab', 'patient']


class BillSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True)

    class Meta:
        model = Bills
        fields = ['id', 'tests', 'payment_mode', 'advance', 'payment_status', 'total_amount', 'due',
                  'lab', 'patient', 'created_at']
        read_only_fields = ['payment_status', 'total_amount', 'due', 'created_at', 'lab', 'patient']


class CBCTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBCTest
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['id', 'lab', 'test']


class UrinalysisTestSerializers(serializers.ModelSerializer):
    class Meta:
        model = UrinalysisTest
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['id', 'lab', 'test']


class CholesterolProfileTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CholesterolProfileTest
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['id', 'lab', 'test']


class LiverFunctionTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiverFunctionTest
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['id', 'lab', 'test']
