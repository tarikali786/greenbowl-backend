from rest_framework import serializers
from account.models import Account

class VarifyNumberSerializer(serializers.Serializer):
    phone = serializers.CharField()


class AccountSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['uid','name',"phone","profile"]