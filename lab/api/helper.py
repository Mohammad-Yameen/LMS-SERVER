from datetime import datetime
import pdfkit
import pytz

from lab.models import CBCTest, UrinalysisTest, CholesterolProfileTest, LiverFunctionTest
from .serializers import CBCTestSerializer, UrinalysisTestSerializers, LiverFunctionTestSerializer, \
    CholesterolProfileTestSerializer

from django.template.loader import get_template
from django.http import HttpResponse


def get_bill_payload(request, payload, patient):
    total_amount = 0
    for test in payload['tests']:
        total_amount += test['price']

    due_amount = total_amount - payload['advance']
    payment_status = 'due'
    if not due_amount:
        payment_status = 'paid'

    bill_payload = {
        "payment_mode": payload['payment_mode'],
        "payment_status": payment_status,
        "total_amount": total_amount,
        "due": due_amount,
        "advance": payload['advance'],
        "patient": patient,
        "lab_user": request.user.labuser,
        "lab": request.user.labuser.lab
    }

    return bill_payload


def calculate_age(dob):
    try:
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return None


def get_indian_current_time_formatted():
    indian_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(indian_timezone)
    return current_time.strftime('%m/%d/%y, %I:%M %p')


def get_bill_context(bill):
    patient = bill.lab_patient
    tests = bill.tests_set.all()
    return {
        'bill_id': bill.id,
        'patient_name': f'{patient.first_name}',
        'patient_gender': patient.gender,
        'patient_age': calculate_age(patient.dob),
        'payment_mode': bill.payment_mode,
        'date_time': get_indian_current_time_formatted(),
        'tests': tests,
        'total_amount': bill.total_amount,
        'advance': bill.advance,
        'due': bill.due
    }


def generate_pdf_response(template, context):
    template = get_template(template)
    html = template.render(context)
    pdf = pdfkit.from_string(html, False)

    filename = "patient_bill.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="' + filename + '"'
    return response


test_mapping = {
    'cbc': CBCTest,
    'liver function': LiverFunctionTest,
    'cholesterol profile': CholesterolProfileTest,
    'urinalysis': UrinalysisTest
}

test_serializer_mapping = {
    'cbc': CBCTestSerializer,
    'liver function': LiverFunctionTestSerializer,
    'cholesterol profile': CholesterolProfileTestSerializer,
    'urinalysis': UrinalysisTestSerializers
}


def get_units_and_ref_range(test_type):
    units_and_ref_range = {
        "cbc": [
            {"parameter": "hemoglobin", "units": "g/dL", "ref_range": "13.5-17.5 g/dL"},
            {"parameter": "wbc_count", "units": "cells/µL", "ref_range": "4,500-11,000 cells/µL"},
            {"parameter": "rbc_count", "units": "cells/µL", "ref_range": "4.7-6.1 million cells/µL"},
            {"parameter": "platelet_count", "units": "platelets/µL", "ref_range": "150,000-450,000 platelets/µL"},
        ],
        "urinalysis": [
            {"parameter": "color", "units": "NA", "ref_range": "Clear to light yellow"},
            {"parameter": "appearance", "units": "NA", "ref_range": "Clear"},
            {"parameter": "ph", "units": "NA", "ref_range": "4.5-8.0"},
        ],
        "cholesterol profile": [
            {"parameter": "total_cholesterol", "units": "mg/dL", "ref_range": "125-200 mg/dL"},
            {"parameter": "hdl_cholesterol", "units": "mg/dL", "ref_range": "40-60 mg/dL"},
            {"parameter": "ldl_cholesterol", "units": "mg/dL", "ref_range": "Men: <100 mg/dL, Women: <130 mg/dL"},
            {"parameter": "triglycerides", "units": "mg/dL", "ref_range": "Men: <150 mg/dL, Women: <175 mg/dL"},
        ],
        "liver function": [
            {"parameter": "alt", "units": "U/L", "ref_range": "<40 U/L"},
            {"parameter": "ast", "units": "U/L", "ref_range": "<40 U/L"},
            {"parameter": "total_bilirubin", "units": "mg/dL", "ref_range": "0.2-1.0 mg/dL"},
            {"parameter": "direct_bilirubin", "units": "mg/dL", "ref_range": "0.0-0.2 mg/dL"},
        ]
    }

    return units_and_ref_range.get(test_type)


def make_test_context(tests_params, patient):
    result = []
    for test in tests_params:
        params = get_units_and_ref_range(test_type=test.test_name)
        for param in params:
            param.update({"value": test.__dict__[param['parameter']]})
        params.insert(0, [])
        result.append({"parameters": params, "test_name": test.test_name})

    return {
        "patient_name": f'{patient.first_name} {patient.last_name}',
        "date_time": get_indian_current_time_formatted(),
        "tests": result

    }
