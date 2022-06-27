'''
Основные сущности:
- Location - место для работы специалиста. В одном месте в одно время 
может работать только один специалист.
- Worker - специалист, предоставляющий услугу.
- Schedule - временной отрезок работы специалиста.
Для каждого рабочего дня можно устанавливать отдельный отрезок, также 
в один день можно установить несколько рабочих отрезков (например, 
с 8:00 до 10:00 и с 17:00 до 21:00 того же дня).
- Appointment - забронированная запись на прием, создаваемая администратором. 
Запись содержит время начала и время конца (разные процедуры могут 
занимать разное время).
'''

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

WEEK = (
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday"),            
        ) # choises of the days in Schedule

class Users(AbstractUser):
    '''
    Users for authentication
    '''
    is_admin = models.BooleanField(default=False)
    is_serviceman = models.BooleanField(default=False)

class Location(models.Model):
    '''
    Location (rooms) for working
    '''
    room = models.IntegerField(u'Room number', unique=True, db_index=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.room) + " : " + self.name

class Worker(models.Model):
    ''''
    People who work there
    '''
    name = models.CharField(u'Name, surname', max_length=255, db_index=True, blank=False)
    speciality = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    ''''
    Weekly schedule of workers, has checking for time crossing
    '''
    worker = models.ForeignKey(Worker, verbose_name=u'Staff', 
                            related_name='worker_Schedule', 
                            on_delete=models.CASCADE, blank=False)
    day = models.IntegerField(u'Day of the week', choices=WEEK, 
                            null=False, blank=False)
    time_in = models.TimeField(u'Starting time', help_text=u'Starting time', 
                            db_index=True, blank=False)
    time_out = models.TimeField(u'Final time', help_text=u'Final time', 
                            db_index=True, blank=False)

    class Meta:
        verbose_name = u'Scheduling'
        verbose_name_plural = u'Scheduling'    

    def clean(self) -> None:
        
        super().clean_fields()

        # implement checking for time crossing
        if self.time_out <= self.time_in:
            raise ValidationError('Ending hour must be after the starting hour')
        
        if not Worker.objects.filter(name = self.worker.name):
            raise ValidationError('Wrong staff')
        
        if self.day < 1 or self.day > 7: raise ValidationError('Wrong day')

        events_worker = check_overlap(self, Schedule.objects.
                                    filter(worker = self.worker).
                                    filter(day = self.day))

        if events_worker.exists():
            raise ValidationError(
                'There is an overlap with another event: ' + str(
                    events_worker[0].day) + ', ' + str(
                    events_worker[0].time_in) + '-' + str(
                    events_worker[0].time_out))

        return super().clean()

class Appointments(models.Model):
    '''
    Appointments to visit workers according to the schedule, has checking for time crossing
    '''

    number = models.IntegerField(unique=True, db_index=True)
    worker = models.ForeignKey(Worker, related_name='worker', 
                            on_delete=models.CASCADE, blank=False)
    place = models.ForeignKey(Location, related_name='place', 
                            on_delete=models.CASCADE, blank=False)
    day = models.DateField(u'Day', db_index=True, blank=False)
    time_in = models.TimeField(u'Starting time', help_text=u'Starting time', 
                            db_index=True, blank=False)
    time_out = models.TimeField(u'Final time', help_text=u'Final time', 
                            db_index=True, blank=False)
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(Users, related_name='creator', null=True, 
                            on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'Appointment'
        verbose_name_plural = u'Appointments'

    def clean(self) -> None:

        super().clean_fields()

        # implement checking for time crossing
        if self.time_out <= self.time_in:
            raise ValidationError('Ending hour must be after the starting hour')
        
        events_place = check_overlap(self, Appointments.objects.filter(place = self.place))
        events_worker = check_overlap(self, Appointments.objects.filter(worker = self.worker))
        if events_place.exists():
            raise ValidationError(
                'There is an overlap with another event: ' + 
                    str(events_place[0].worker) + ', ' + str(
                    events_place[0].time_in) + '-' + str(events_place[0].time_out))
        elif events_worker.exists():
            raise ValidationError(
                'There is an overlap with another event: ' + 
                    str(events_worker[0].place) + ', ' + str(
                    events_worker[0].time_in) + '-' + str(events_worker[0].time_out))
        
        events_schedule = Schedule.objects.filter(worker = self.worker
                                        ).filter(day = self.day.isoweekday()
                                        ).filter(time_in__lte = self.time_in
                                        ).filter(time_out__gte = self.time_out)
        if not events_schedule.exists():
            raise ValidationError('There are no working hours in that time: ')

        return super().clean()

def check_overlap(self_events, events):
    '''
    Helper function for the time crossing

            Parameters:
                    self_events (Model): New model with data to add to the database
                    events (QuerySet): QuerySet with another entries 

            Returns:
                    QuerySet (empty if no time crossing, with data if have time crossing)
    '''
    if not events.exists(): return events
    events_1 = events.filter(time_in__gte = self_events.time_in
                            ).filter(time_in__lt = self_events.time_out)
    events_2 = events.filter(time_out__gt = self_events.time_in
                            ).filter(time_out__lte = self_events.time_out)
    events_3 = events.filter(time_in__lte = self_events.time_in
                            ).filter(time_out__gte = self_events.time_out)
    if events_1.exists(): return events_1
    elif events_2.exists(): return events_2
    elif events_3.exists(): return events_3
    else: return events_1


