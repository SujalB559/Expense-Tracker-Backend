from rest_framework import serializers
from .models import Category
from .utils import CATEGORY_ICONS


class CategorySerializer(serializers.ModelSerializer):
    limit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'type',
            'icon',
            'is_default',
            'limit',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        name = attrs.get('name') or (self.instance.name if self.instance else '')
        category_type = attrs.get('type') or (self.instance.type if self.instance else 'expense')

        if not self.instance:
            if Category.objects.filter(user=user, name__iexact=name, type=category_type).exists():
                raise serializers.ValidationError(
                    f"A category named '{name}' already exists in {category_type} categories."
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        name = validated_data.get('name', '').strip()
        icon = validated_data.get('icon', '').strip()
        if not icon:
            icon = CATEGORY_ICONS.get(name, '🏷️')
            validated_data['icon'] = icon

        validated_data['user'] = request.user
        validated_data['is_default'] = False
        return super().create(validated_data)
