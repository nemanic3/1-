from rest_framework import serializers

class GraduationStatusSerializer(serializers.Serializer):
    total_completed = serializers.IntegerField()
    total_required = serializers.IntegerField()

    major_completed = serializers.IntegerField()
    major_required = serializers.IntegerField()

    general_completed = serializers.IntegerField()
    general_required = serializers.IntegerField()

    drbol_completed = serializers.IntegerField()
    drbol_required = serializers.IntegerField()

    sw_completed = serializers.IntegerField()
    sw_required = serializers.IntegerField()

    msc_completed = serializers.IntegerField()
    msc_required = serializers.IntegerField()

    special_general_completed = serializers.IntegerField()
    special_general_required = serializers.IntegerField()

    missing_major_courses = serializers.ListField(child=serializers.CharField())
    missing_drbol_areas = serializers.ListField(child=serializers.CharField())

    graduation_status = serializers.CharField()
    message = serializers.CharField()
