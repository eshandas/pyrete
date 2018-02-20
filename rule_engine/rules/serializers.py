"""
Serializers
"""

from rest_framework import serializers
from .models import Rule
import json


class ThenSerializer(serializers.Serializer):
    key = serializers.CharField(
        max_length=255,
        required=True)
    trigger_type = serializers.ChoiceField(
        choices=('webhook', 'loyalty_event'))
    webhook_details = serializers.DictField(
        required=False)
    params = serializers.DictField()


class WhenSerializer(serializers.Serializer):
    any = serializers.ListField(
        child=serializers.DictField())
    all = serializers.ListField(
        child=serializers.DictField())


class RuleSerializer(serializers.Serializer):
    key = serializers.CharField(
        max_length=255,
        required=True)
    description = serializers.CharField(
        required=True)
    rule = serializers.CharField(
        required=True)

    class Meta:
        model = Rule
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'key': obj.key,
            'description': obj.description,
            'rule': json.loads(obj.rule)}
