from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'initials',
            'currency',
            'theme',
            'is_email_verified',
            'date_joined',
        ]
        read_only_fields = ['id', 'is_email_verified', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    user = UserSerializer(source='*', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'currency',
            'theme',
            'user',
        ]
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'currency': {'required': False},
            'theme': {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop('password')
        # New users start unverified
        user = User.objects.create_user(password=password, is_email_verified=False, **validated_data)

        # Seed initial default categories and monthly budget for new user
        from categories.utils import seed_default_categories
        from budgets.models import MonthlyBudget

        seed_default_categories(user)
        MonthlyBudget.objects.get_or_create(user=user, defaults={'amount': 2000.00})

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        if not username_or_email or not password:
            raise serializers.ValidationError("Both username and password are required.")

        # Allow login with either username or email
        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials. Please check your username and password.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")

        attrs['user'] = user
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'currency',
            'theme',
        ]

    def validate_email(self, value):
        request = self.context.get('request')
        current_user = request.user if request else None
        if User.objects.filter(email__iexact=value).exclude(pk=current_user.pk if current_user else None).exists():
            raise serializers.ValidationError("This email is already in use by another account.")
        return value.lower()
