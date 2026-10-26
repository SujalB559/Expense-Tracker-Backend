from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers

from .models import MonthlyBudget, SavingsGoal


class MonthlyBudgetSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField()
    spent_this_month = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percent_used = serializers.SerializerMethodField()
    is_warning = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyBudget
        fields = [
            'amount',
            'spent_this_month',
            'remaining',
            'percent_used',
            'is_warning',
            'updated_at',
        ]
        read_only_fields = ['updated_at']

    def get_spent_this_month(self, obj):
        now = datetime.now()
        spent = obj.user.transactions.filter(
            type='expense',
            date__year=now.year,
            date__month=now.month,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return float(spent)

    def get_remaining(self, obj):
        spent = self.get_spent_this_month(obj)
        budget = float(obj.amount)
        return max(0.0, budget - spent)

    def get_percent_used(self, obj):
        spent = self.get_spent_this_month(obj)
        budget = float(obj.amount)
        if budget > 0:
            return min(round((spent / budget) * 100), 100)
        return 0

    def get_is_warning(self, obj):
        spent = self.get_spent_this_month(obj)
        budget = float(obj.amount)
        if budget > 0:
            return (spent / budget) >= 0.8
        return False


class SavingsGoalSerializer(serializers.ModelSerializer):
    target = serializers.FloatField()
    saved = serializers.FloatField(default=0.0)
    progress = serializers.ReadOnlyField()

    class Meta:
        model = SavingsGoal
        fields = [
            'id',
            'name',
            'target',
            'saved',
            'progress',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_target(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than 0.")
        return value

    def validate_saved(self, value):
        if value < 0:
            raise serializers.ValidationError("Saved amount cannot be negative.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)
