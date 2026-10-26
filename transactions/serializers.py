from decimal import Decimal
from rest_framework import serializers
from categories.models import Category
from categories.utils import CATEGORY_ICONS
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'name',
            'amount',
            'type',
            'category',
            'date',
            'description',
            'recurring',
            'repeat',
            'icon',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount must be greater than or equal to 0.")
        return value

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Transaction name cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        validated_data['user'] = user

        # Resolve icon automatically if missing
        icon = validated_data.get('icon', '').strip()
        category_name = validated_data.get('category', '').strip()
        if not icon and user:
            # Check user categories first
            cat_obj = Category.objects.filter(user=user, name__iexact=category_name).first()
            if cat_obj and cat_obj.icon:
                icon = cat_obj.icon
            else:
                icon = CATEGORY_ICONS.get(category_name, '🏷️')
        elif not icon:
            icon = CATEGORY_ICONS.get(category_name, '🏷️')

        validated_data['icon'] = icon
        return super().create(validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Ensure date is string formatted as YYYY-MM-DD
        if instance.date:
            ret['date'] = instance.date.strftime('%Y-%m-%d')
        # Amount as float
        ret['amount'] = float(instance.amount)
        return ret
