from rest_framework import serializers
from .models import Users, Location, Worker, Schedule, Appointments

class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Location
        fields = '__all__'

class WorkerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Worker
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Schedule
        fields = '__all__'

class AppointmentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointments
        fields = '__all__'

