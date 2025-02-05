from rest_framework import serializers

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    description = serializers.CharField(max_length=255, required=True)
    fname = serializers.CharField(max_length=100, required=True)
    lname = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=10, required=True)
    address = serializers.DictField(
        child=serializers.CharField(max_length=255),
        required=True
    )
