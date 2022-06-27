# Generated by Django 4.0.5 on 2022-06-26 08:28

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_serviceman', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.IntegerField(db_index=True, unique=True, verbose_name='Room number')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='Name, surname')),
                ('speciality', models.CharField(db_index=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], verbose_name='Day of the week')),
                ('time_in', models.TimeField(db_index=True, help_text='Starting time', verbose_name='Starting time')),
                ('time_out', models.TimeField(db_index=True, help_text='Final time', verbose_name='Final time')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker_Schedule', to='sched_api.worker', verbose_name='Staff')),
            ],
            options={
                'verbose_name': 'Scheduling',
                'verbose_name_plural': 'Scheduling',
            },
        ),
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True, unique=True)),
                ('day', models.DateField(db_index=True, verbose_name='Day')),
                ('time_in', models.TimeField(db_index=True, help_text='Starting time', verbose_name='Starting time')),
                ('time_out', models.TimeField(db_index=True, help_text='Final time', verbose_name='Final time')),
                ('title', models.CharField(max_length=255)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place', to='sched_api.location')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker', to='sched_api.worker')),
            ],
            options={
                'verbose_name': 'Appointment',
                'verbose_name_plural': 'Appointments',
            },
        ),
    ]