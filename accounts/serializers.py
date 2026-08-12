from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "phone_number",
            "user_role",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class MeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
            "bio",
            "skills",
            "education",
            "experience",
            "resume",
            "user_role",
            "is_verified",
        ]

        read_only_fields = [
            "id",
            "email",
            "user_role",
            "is_verified",
        ]

    def validate_resume(self, value):
        if value is None:
            return value

        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
        ]

        extension = value.name.lower()

        if not any(extension.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "Resume must be a PDF, DOC, or DOCX file."
            )

        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Resume file size must not exceed 5 MB."
            )

        return value