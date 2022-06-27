from django_filters.rest_framework import FilterSet, ModelChoiceFilter
from django_tables2 import Table, Column
from.models import Schedule, Worker

from django.forms import Select

class ScheduleFilter(FilterSet):
    '''
    For filter in schedule table
    '''
    worker__speciality = ModelChoiceFilter(label='Speciality', queryset= Worker.objects.
                                values_list('speciality', flat=True).distinct(), 
                                widget=Select, to_field_name = 'speciality')

    class Meta:
        model = Schedule
        fields = ('worker', 'worker__speciality', 'day', 'time_in', 'time_out' )


class ScheduleTable(Table):  
    '''
    Add to default Schedule table s[eciality of workers
    '''
    id = Column()
    worker = Column()
    worker__speciality = Column()
    day = Column()
    time_in = Column()
    time_out = Column()
    
    class Meta:
        ordering = 'description'
        #model = Schedule
        
