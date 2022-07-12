from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Schedule, Worker, Location, Appointments, Users
from .models import check_overlap
from .forms import WorkerForm, LocationForm, ScheduleForm, AppointmentsForm
from .views import api_admin_add_staff
from .serializers import (UsersSerializer, WorkerSerializer, 
                    LocationSerializer, ScheduleSerializer, AppointmentsSerializer)
import datetime
from django.contrib.auth import get_user_model

class ModelTest(TestCase):
    '''
    Models testing
    '''
    worker = location = schedule = appointments = user = ''
    
    def setUp(self):
        # Create auxiliary data
        ModelTest.worker = Worker.objects.create(name='test worker', speciality = 'test dantist')
        ModelTest.worker.save()
        ModelTest.location = Location.objects.create(name='test place', room = 2)
        ModelTest.location.save()
        ModelTest.schedule = Schedule.objects.create(worker = ModelTest.worker, day = '1',
                                         time_in = "11:00", time_out = "18:00")
        ModelTest.schedule.save()
        ModelTest.user = Users.objects.create(username='test', password='222',
                                        is_active=True, is_serviceman=True, is_admin=True, 
                                        is_staff=False, is_superuser=False)
        ModelTest.user.save()
        ModelTest.appointments = Appointments.objects.create(number=2, worker=ModelTest.worker,
                                        place=ModelTest.location, day=datetime.date(2022,6,20), time_in='12:00',
                                        time_out='14:00', title='test_app', 
                                        creator=ModelTest.user)
        ModelTest.appointments.save()
        super().setUp()                                        

    def test_create_model(self):
        # check creation
        self.assertTrue(isinstance(ModelTest.worker, Worker))
        self.assertTrue(isinstance(ModelTest.location, Location))        
        self.assertTrue(isinstance(ModelTest.schedule, Schedule))
        self.assertTrue(isinstance(ModelTest.appointments, Appointments))
        self.assertEqual(ModelTest.worker.name, 'test worker')
        self.assertEqual(ModelTest.schedule.time_in, "11:00")
        self.assertEqual(ModelTest.location.room, 2)
        self.assertEqual(ModelTest.appointments.day, datetime.date(2022,6,20))

    def test_overlap_time_in_schedule(self):
        # check overlap function in schedule
        class Test_Class:
            time_in = '12:22'
            time_out = '13:22'
        self.assertTrue(check_overlap(Test_Class, Schedule.objects.filter()).exists())        
        Test_Class.time_in = '10:00'
        Test_Class.time_out = '11:10'
        self.assertTrue(check_overlap(Test_Class, Schedule.objects.filter()).exists())        
        Test_Class.time_in = '14:00'
        Test_Class.time_out = '18:00'
        self.assertTrue(check_overlap(Test_Class, Schedule.objects.filter()).exists())
        Test_Class.time_in = '19:00'
        Test_Class.time_out = '20:00'
        self.assertTrue(not check_overlap(Test_Class, Schedule.objects.filter()).exists())
        schedule_wrong_time = Schedule(worker = ModelTest.worker, day = '1', 
                                                    time_in = "17:00", time_out = "15:00")
        with self.assertRaises(ValidationError):
            schedule_wrong_time.clean()

    def test_overlap_time_in_appointments(self):
        # check overlap function in appointments
        class Test_Class:
            time_in = '12:22'
            time_out = '13:22'
        self.assertTrue(check_overlap(Test_Class, Appointments.objects.filter()).exists())        
        Test_Class.time_in = '10:00'
        Test_Class.time_out = '12:10'
        self.assertTrue(check_overlap(Test_Class, Appointments.objects.filter()).exists())        
        Test_Class.time_in = '13:50'
        Test_Class.time_out = '18:00'
        self.assertTrue(check_overlap(Test_Class, Appointments.objects.filter()).exists())
        Test_Class.time_in = '10:00'
        Test_Class.time_out = '11:30'
        self.assertTrue(not check_overlap(Test_Class, Appointments.objects.filter()).exists())
        appointment_all_good = Appointments(number=3, worker=ModelTest.worker,
                                        place=ModelTest.location, day=datetime.date(2022,6,20), time_in='11:10',
                                        time_out='11:50', title='test_app_2', creator=ModelTest.user)
        appointment_all_good.clean()
        # self.assertRaises(ValidationError, appointment_all_good.full_clean)
        appointment_wrong_time = Appointments(number=4, worker=ModelTest.worker,
                                        place=ModelTest.location, day=datetime.date(2022,6,20), time_in='16:00',
                                        time_out='15:00', title='test_app_3', creator=ModelTest.user)
        with self.assertRaises(ValidationError):
            appointment_wrong_time.clean()
        appointment_wrong_time_2 = Appointments(number=5, worker=ModelTest.worker,
                                        place=ModelTest.location, day=datetime.date(2022,6,20), time_in='13:00',
                                        time_out='16:00', title='test_app_4', creator=ModelTest.user)
        with self.assertRaises(ValidationError):
            appointment_wrong_time_2.clean()
        appointment_wrong_day = Appointments(number=6, worker=ModelTest.worker,
                                        place=ModelTest.location, day=datetime.date(2022,6,21), time_in='16:00',
                                        time_out='17:00', title='test_app_5', creator=ModelTest.user)
        with self.assertRaises(ValidationError):
            appointment_wrong_day.clean()

class ViewTest(TestCase):

    def test_list_view(self):
        '''
        Rendering testing
        '''
        # Worker
        worker_test = ModelTest.worker
        worker_test.save()
        url = reverse("html_workers")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(worker_test.name, resp.content.decode())

        #Location
        place_test = ModelTest.location
        place_test.save()

        # Schedule
        schedule_test = ModelTest.schedule
        schedule_test.save()
        url = reverse("html_schedule")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(schedule_test.time_in, resp.content.decode())

        # Users
        user_test = ModelTest.user
        user_test.save()

        # Appointments
        appointments_test = ModelTest.appointments
        appointments_test.save()
        url = reverse("html_view_appointments")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(appointments_test.title, resp.content.decode())
    
    def test_forms(self):
        '''
        Forms testing
        '''
        # Valid
        data = {'name': ModelTest.worker.name, 'speciality': ModelTest.worker.speciality}
        form = WorkerForm(data=data)
        self.assertTrue(form.is_valid())

        data = {'name': ModelTest.location.name, 'room': ModelTest.location.room}
        form = LocationForm(data=data)
        self.assertTrue(form.is_valid())

        ModelTest.schedule.worker.save()
        data = {'worker': ModelTest.schedule.worker, 'day': ModelTest.schedule.day, 
                'time_in': ModelTest.schedule.time_in, 'time_out': ModelTest.schedule.time_out}
        form = ScheduleForm(data=data)
        self.assertTrue(form.is_valid())

        ModelTest.appointments.worker.save()
        ModelTest.appointments.place.save()
        ModelTest.appointments.creator.save()
        ModelTest.schedule.save()
        ModelTest.user.save()
        data = {'number':ModelTest.appointments.number+10, 'worker':ModelTest.appointments.worker, 
                'place':ModelTest.appointments.place, 'day':datetime.date(2022,6,20), 
                'time_in':"11:00", 'time_out':"11:30", 
                'title':'test_app_2', 'creator':ModelTest.user}
        form = AppointmentsForm(data=data)
        form.fields['creator'].disabled = False
        self.assertTrue(form.is_valid())           

        # Invalid
        data = {'name': '', 'speciality': ModelTest.worker.speciality,}
        form = WorkerForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'name': ModelTest.location.name, 'room': 'qqq',}
        form = LocationForm(data=data)
        self.assertFalse(form.is_valid())

        data = {'worker': '', 'day': ModelTest.schedule.day, 
                'time_in': ModelTest.schedule.time_in, 'time_out': ModelTest.schedule.time_out}
        form = ScheduleForm(data=data)
        self.assertFalse(form.is_valid())    

        data = {'number':ModelTest.appointments.number+10, 'worker':ModelTest.appointments.worker, 
                'place':ModelTest.appointments.place, 'day':datetime.date(2022,6,21), 
                'time_in':"11:00", 'time_out':"11:30", 
                'title':'test_app_2', 'creator':ModelTest.user}
        form = AppointmentsForm(data=data)
        form.fields['creator'].disabled = False
        self.assertFalse(form.is_valid())

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret',
            'is_admin': True,
            'is_serviceman': True}
        Users.objects.create_user(**self.credentials)

    def test_creation_via_request(self):
        '''
        Test creation data in models using requests
        '''
        # send login data
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)

        # Test worker creation
        data = {'name': 'test api worker', 'speciality': 'test api dantist'}
        response = self.client.post(reverse('api_admin_worker'), data)
        # response.context['message']
        self.assertEqual(Worker.objects.filter()[0].name, 'test api worker')

        # Test location creation
        data = {'name': 'test api location', 'room': 123}
        response = self.client.post(reverse('api_admin_location'), data)
        self.assertEqual(Location.objects.filter()[0].name, 'test api location')

        # Test schedule creation
        data = {'worker': '1', 'day': '5', 
                'time_in': "11:11", 'time_out': "22:22"}
        response = self.client.post(reverse('api_admin_schedule'), data)
        self.assertEqual(Schedule.objects.filter()[0].time_in, datetime.time(11,11))

        # Test appointments creation
        data = {'number': '1', 'worker': '1', 'place': '1', 
                'day':datetime.date(2022,6,24), 'time_in':"11:22", 'time_out':"11:30", 
                'title':'test_app_2', 'creator': '1'}
        response = self.client.post(reverse('api_admin_appointments'), data)
        self.assertEqual(Appointments.objects.filter()[0].time_in, datetime.time(11,22))

class SerializersTest(TestCase):
    '''
    Serializers tests
    '''

    def test_serializer(self):
        user = UsersSerializer()
        user.create({'username':'testuser', 'password':'testpass'})
        self.assertEqual(UsersSerializer(Users.objects.filter(username='testuser'),
                         many=True).data[0]['password'],'testpass') # check correct
        self.assertEqual(len(Users.objects.filter(username='wronguser')),0) # check mistake

        location = LocationSerializer()
        location.create({'name':'testname', 'room':1})
        self.assertEqual(LocationSerializer(Location.objects.filter(name='testname'),
                         many=True).data[0]['room'],1) # check correct
        self.assertEqual(len(Location.objects.filter(room=2)),0) # check mistake

        worker = WorkerSerializer()
        worker.create({'name':'testname', 'speciality':'test_spec'})
        self.assertEqual(WorkerSerializer(Worker.objects.filter(name='testname'),
                         many=True).data[0]['speciality'],'test_spec') # check correct
        self.assertNotEqual(WorkerSerializer(Worker.objects.filter(name='testname'),
                         many=True).data[0]['speciality'],'wrong') # check wrong                         
        self.assertEqual(len(Worker.objects.filter(name='wrong')),0) # check mistake

        schedule = ScheduleSerializer()
        schedule.create({'worker':Worker.objects.get(pk=1), 'day':1, 'time_in':'11:00', 'time_out':'22:00'})
        self.assertEqual(ScheduleSerializer(Schedule.objects.filter(time_in='11:00'),
                         many=True).data[0]['time_out'],'22:00:00') # check correct
        self.assertNotEqual(ScheduleSerializer(Schedule.objects.filter(time_in='11:00'),
                         many=True).data[0]['time_out'],'11:00') # check wrong
        self.assertEqual(len(Schedule.objects.filter(day=2)),0) # check mistake
