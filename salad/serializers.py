from rest_framework import serializers

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    address = serializers.DictField(child=serializers.CharField(), required=True)