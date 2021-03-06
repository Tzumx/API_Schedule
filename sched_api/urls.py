from django.urls import path
from .views import api_view_workers, api_worker_schedule, log_out, api_view_appointments
from .views import api_admin_worker, api_admin_location, api_admin_schedule, api_admin_appointments
from .views import LogInView, SignUpView, UserList, WorkerList, ScheduleList, AppointmentList
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('workers', api_view_workers, name='html_workers'), # List of workers
    path('schedule', api_worker_schedule, name='html_schedule'), # List worker's schedule
    path('appointments', api_view_appointments, name='html_view_appointments'),

    path('admin', SignUpView.as_view(), name='admin'), # Add administrations
    path('login', LogInView.as_view(), name='login'), # Login
    path('logout', log_out, name='logout'), # Logout

    # Add different information to specific tables
    path('api_admin_worker', api_admin_worker, name='api_admin_worker'),
    path('api_admin_location', api_admin_location, name='api_admin_location'),
    path('api_admin_schedule', api_admin_schedule, name='api_admin_schedule'),
    path('api_admin_appointments', api_admin_appointments, name='api_admin_appointments'),

    path('api/users', UserList.as_view(), name = 'api_users'),
    path('api/workers', WorkerList.as_view(), name = 'api_workers'),
    # path('api/schedule', api_worker_schedule, {'type_result': 'json'}, name='api_schedule'),
    path('api/schedule', ScheduleList.as_view(), name='api_schedule'),
    path('api/appointments', AppointmentList.as_view(), name='api_view_appointments'),

]
