from shop.models import Client
from rest_framework import serializers

class ClientSerilizer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('url', 'username', 'lastname', 'firstname', 'middlename', 'address', 'tel')
        