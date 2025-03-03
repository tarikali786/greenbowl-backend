from rest_framework import serializers
from account.models import Account, UserAddress
from salad.serializers import *
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



class UserAddressSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ['user']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'

class UserDetailSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    orders = UserOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['name','email', 'profile', 'addresses','uid','gender','phone','orders']
        