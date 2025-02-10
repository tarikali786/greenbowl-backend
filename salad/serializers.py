from rest_framework import serializers

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    