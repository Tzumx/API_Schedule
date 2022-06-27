from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Appointments, Worker, Users, Schedule
from .serializers import AppointmentsSerializer, WorkerSerializer, ScheduleSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.generic import CreateView, View
from django.shortcuts import redirect
from .forms import SignUpForm, LogInForm, WorkerForm, LocationForm, ScheduleForm, AppointmentsForm
from django.contrib.auth import authenticate, logout
from .decorators import serviceman_required, admin_required
from django.utils.decorators import method_decorator
from .filters import ScheduleFilter, ScheduleTable

@api_view(['GET', ])
def api_view_workers(request, type_result='html'):
    '''
    Get the list of specialists

            Parameters:
                    request (Request): Request with parameters
                    type_result (str): parameter to choose type of exit data

            Returns:
                   Form for rendering in templates or JSON with data    
    '''  
    message = "List of workers"
    worker_speciality = request.data['speciality'] if len(request.data)>0 else ''
    if worker_speciality != '': workers_list = Worker.objects.filter(speciality=worker_speciality)
    else: workers_list = Worker.objects.filter()

    serialized_workers_list = WorkerSerializer(workers_list, many=True)

    if type_result == 'html':
        return render(request, 'view_list.html', context={'data': workers_list, 'message': message})
    else: return JsonResponse(serialized_workers_list.data, safe=False)


@api_view(['GET', ])
def api_worker_schedule(request, type_result='html'):
    '''
    Get the specilist's schedule

            Parameters:
                    request (Request): Request with parameters
                    type_result (str): parameter to choose type of exit data

            Returns:
                   Form for rendering in templates or JSON with data    
    '''      
    worker_speciality = request.data['speciality'] if len(request.data)>0 else ''
    day_schedule = (request.data['day']).isoweekday() if len(request.data)>0 else 0

    worker_speciality_list = Schedule.objects.filter(worker__speciality = worker_speciality) if (
        not worker_speciality == '') else Schedule.objects.filter()
    
    worker_day_schedule = worker_speciality_list.filter(day = day_schedule) if (
        not day_schedule == 0) else worker_speciality_list

    filter = ScheduleFilter(request.GET, queryset = worker_speciality_list)
    data = ScheduleTable(data=filter.qs)
    serialized_schedule_list = ScheduleSerializer(worker_day_schedule, many=True)
    
    if type_result == 'html':
        return render(request, 'schedule.html', context={'filter': filter, 'data': data})
    else: return JsonResponse(serialized_schedule_list.data, safe=False)

def api_view_appointments(request, type_result='html'):
    '''
    Get the list of appointments

            Parameters:
                    request (Request): Request with parameters
                    type_result (str): parameter to choose type of exit data

            Returns:
                   Form for rendering in templates or JSON with data    
    '''      
    message = "List of appointments"
    appointments_list = Appointments.objects.all()
    serialized_appointments_list = AppointmentsSerializer(appointments_list, many=True)

    if type_result == 'html':
        return render(request, 'view_list.html', context={'data': appointments_list, 'message': message})
    else: return JsonResponse(serialized_appointments_list.data, safe=False)


# @api_view(['GET', 'POST'])
# # @permission_classes([IsAuthenticated])
# # @login_required(login_url='/login/')
# @admin_required
# def api_admin(request):
#     if request.user.is_authenticated: return JsonResponse({'work':'it'})
#     else: return JsonResponse({"don't":"work"})

def api_admin_add_staff(request, form_model, staff, initial={}):
    '''
    Add data in different models

            Parameters:
                    request (Request): Request with parameters
                    form_model (ModelForm): Model in which we add data
                    staff (str): Information for rendering in template
                    initial (dict): parameters for initial value in rendered forms

            Returns:
                   Form for rendering in templates   
    '''     
    form = form_model(data = request.POST, initial = initial)
    message = ''

    if request.method == 'POST':
        if form.is_valid(): # check for valid data in table's fields before saving
            form.save()
            message = "Saved"
            render(request, 'add_staff.html', context={'form': form_model(initial = initial),
                 'message': message, 'staff': staff})
        else:
            message = 'Invalid fields'
    return render(request, 'add_staff.html', {'form': form_model(initial = initial),
                 'message': message, 'staff': staff}) 

@api_view(['GET', 'POST'])
@admin_required
def api_admin_worker(request):
    # Add workers

    answer = api_admin_add_staff(request, WorkerForm, 'worker')
    return answer

@api_view(['GET', 'POST'])
@admin_required
def api_admin_location(request):
    # Add Location
    
    answer = api_admin_add_staff(request, LocationForm, 'location')
    return answer

@api_view(['GET', 'POST'])
@admin_required
def api_admin_schedule(request):
    # Add schedule

    answer = api_admin_add_staff(request, ScheduleForm, 'schedule')
    return answer

@api_view(['GET', 'POST'])
@admin_required
def api_admin_appointments(request):
    # Add appointments
    
    id = Users.objects.filter(username = request.user.username)
    if request.method == 'POST':
        request.POST._mutable = True
        if len(id) == 1: request.POST['creator'] = id[0] # for setting initial value in creator (!delete!)
        request.POST._mutable = False
    elif request.method == 'GET':
        pass
    answer = api_admin_add_staff(request, AppointmentsForm, 'appointments', initial={'creator': id[0]})
    return answer


@method_decorator([serviceman_required], name='dispatch')
class SignUpView(CreateView):
    '''
    Form for adding users
    '''
    model = Users
    form_class = SignUpForm
    template_name = 'signup_form.html'

    def form_valid(self, form):
        user = form.save()
        # login(self.request, user) # login mmediately in new user
        return redirect('admin')

class LogInView(View):
    '''
    Form for Login
    '''
    template_name = 'login_form.html'
    form_class = LogInForm
    
    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})
        
    def post(self, request):
        form = self.form_class(data = request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                next_url  = request.GET.get('next', 'home').replace("/", "")
                return redirect(next_url) # redirect if come from another page
        message = 'Login failed!'
        return render(request, self.template_name, context={'form': form, 'message': message})

def log_out(request):
    # logout
    logout(request)
    return redirect('home')