from django.forms import ChoiceField, ModelForm, TimeInput, DateInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from django.db.models import Max

from .models import Worker, Location, Users, Schedule, Appointments

class SignUpForm(UserCreationForm):
    '''
    Creation users for database
    '''
    access_level = ChoiceField(
        choices = (('is_admin','Admin'), ('is_serviceman','Serviceman'))
    )

    class Meta(UserCreationForm.Meta):
        model = Users

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        if self.cleaned_data['access_level'] == 'is_admin': user.is_admin = True
        if self.cleaned_data['access_level'] == 'is_serviceman': user.is_serviceman = True           
        
        user.save()

        return user


class LogInForm(AuthenticationForm):
    '''
    for login
    '''
    pass

class WorkerForm(ModelForm):
    '''
    Form for Worker Model
    '''
    class Meta:
        model = Worker
        fields = '__all__'

class LocationForm(ModelForm):
    '''
    Form for Location Model
    '''
    class Meta:
        model = Location
        fields = '__all__'

class Time_Input(TimeInput):
    '''
        To format the time entry field
    '''
    input_type = 'time'

class ScheduleForm(ModelForm):
    '''
    Form for Schedule Model
    '''
    class Meta:
        model = Schedule
        fields = '__all__'
        help_texts = {
            'time_in': None,
            'time_out': None,
        }
        widgets = {
            'time_in': Time_Input(), # format entry field
            'time_out': Time_Input(), # format entry field
        }        

class Date_Input(DateInput):
    '''
        To format the date entry field
    '''    
    input_type = 'date'

class AppointmentsForm(ModelForm):
    '''
    Form for Appointments Model
    '''
    class Meta:
        model = Appointments
        fields = '__all__'
        # exclude = ('creator', )
        help_texts = {
            'time_in': None,
            'time_out': None,
        }
        widgets = {
            'day': Date_Input(), # format entry field
            'time_in': Time_Input(), # format entry field
            'time_out': Time_Input(), # format entry field
        }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        max_number = Appointments.objects.aggregate(Max('number')) # set initial number in form
        self.fields['number'].initial = (max_number['number__max'] or 0) + 1
        self.fields['creator'].disabled = True # disable creation field to prevent misdata


    