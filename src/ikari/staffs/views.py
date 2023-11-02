import datetime
import calendar
import json
import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Value
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mail_templated import EmailMessage
from reports.models import Report
from companies.models import Company
from accounting.models import FiscalCalendar, Journal
from accounts.models import AccountHistory
from currencies.models import ExchangeRate
from orders.models import Order
from staffs.forms import UserForm, ChangePasswordForm, GroupForm
from staffs.models import Staff
from staffs.models import Permisson as StaffPermission
from staffs.models import UserPermissions as StaffUserPermissions
from staffs.models import GroupPermissions as StaffGroupPermissions
from django.conf import settings as s
from itertools import chain
import threading
from utilities.constants import TRANSACTION_TYPES, ACCOUNT_TYPE_DICT, STATUS_TYPE_DICT, ST_REPORT_LIST
from utilities.common import round_number


# Create your views here.
def login_redirect(request):
    request.session['login_company_id'] = ''
    request.session['staff_admin'] = 0
    company_list = get_company_list(request)
    if User.is_authenticated:
        return HttpResponsePermanentRedirect(reverse('company_list'))
    else:
        state = "Please log in below..."
        return render_to_response('login.html', RequestContext(request, {'state': state, 'company_list': company_list}))


def get_company_list(request):
    http_host = request.META['HTTP_HOST']
    company_list = Company.objects.filter(is_hidden=0, is_active=True).order_by('name')
    companies = ['nitto', 'crown']
    for company in companies:
        if company in http_host:
            company_list = company_list.filter(name__icontains=company)
            break

    return company_list


def login_do(request):
    username = password = ''
    request.session['login_company_id'] = ''
    request.session['staff_admin'] = 0
    request.session['use_inventory'] = 0
    request.session['session_date'] = None

    company_list = get_company_list(request)

    login_comp = int(request.POST.get('company')) if request.POST.get('company') else 0
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check 3 times login
        login_count = cache.get(username + 'login_count')
        if login_count:
            if int(login_count) >= 3:
                messages_error = "Your username and/or password were incorrect."
                return HttpResponsePermanentRedirect(reverse('reset_confirm'))
        else:
            cache.set(username + 'login_count', 0)

        # Check authenticate
        user = authenticate(username=username, password=password)
        if user is not None:
            # logout other session/device
            # user_sessions = []
            # my_old_sessions = Session.objects.all()
            # for row in my_old_sessions:
            #     if row.get_decoded().get("_auth_user_id") and \
            #         int(row.get_decoded().get("_auth_user_id")) == int(user.id):
            #         user_sessions.append(row.pk)
            # Session.objects.filter(pk__in=user_sessions).delete()

            cache.set(username + 'login_count', 0)
            if request.POST.get('company'):
                request.session['login_company_id'] = request.POST.get('company')
                company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
                company = Company.objects.get(pk=company_id)
                if company.current_period_month_sp and company.current_period_year_sp:
                    currenct_sp_period = datetime.datetime.strptime(company.current_period_month_sp + '-' + company.current_period_year_sp, "%m-%Y").strftime("%m-%Y")
                    request.session['currenct_sp_period'] = currenct_sp_period
                else:
                    request.session['currenct_sp_period'] = datetime.datetime.today().strftime("%m-%Y")
                if company.is_inventory:
                    if company.current_period_month_ic and company.current_period_year_ic:
                        currenct_ic_period = datetime.datetime.strptime(company.current_period_month_ic + '-' + company.current_period_year_ic, "%m-%Y").strftime("%m-%Y")
                        request.session['currenct_ic_period'] = currenct_ic_period
                    else:
                        request.session['currenct_ic_period'] = datetime.datetime.today().strftime("%m-%Y")
                try:
                    request.session['session_date'] = datetime.datetime.strptime(request.POST.get('session_date'), "%Y-%m-%d").date()
                    # fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0,
                    #                         start_date__lte=request.session['session_date'],
                    #                         end_date__gte=request.session['session_date']).first()
                    # if not fsc_calendar:
                    #     fsc_year = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0).values_list('fiscal_year', flat=True).order_by('fiscal_year').distinct().last()
                    #     latest_fsc_data = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, fiscal_year=fsc_year)
                    #     latest_fsc_data = sorted(latest_fsc_data, key=lambda FiscalCalendar: int(FiscalCalendar.period))
                    #     end_date = latest_fsc_data[-1].end_date
                    #     if request.session['session_date'] > end_date:
                    #         new_year = int(fsc_year) + 1
                    #         for data in latest_fsc_data:
                    #             new_calendar = FiscalCalendar()
                    #             new_calendar.fiscal_year = new_year
                    #             new_calendar.period = data.period
                    #             new_calendar.start_date = data.start_date.replace(year=new_year)
                    #             new_calendar.end_date = data.end_date.replace(year=new_year)
                    #             new_calendar.is_ap_locked = False
                    #             new_calendar.is_ar_locked = False
                    #             new_calendar.is_gl_locked = False
                    #             new_calendar.is_bank_locked = False
                    #             new_calendar.is_ic_locked = False
                    #             new_calendar.is_sp_locked = False
                    #             new_calendar.is_adj_locked = False
                    #             new_calendar.is_cls_locked = False
                    #             new_calendar.is_hidden = False
                    #             new_calendar.company_id = company_id
                    #             new_calendar.create_date = datetime.datetime.today()
                    #             new_calendar.update_date = datetime.datetime.today()
                    #             new_calendar.update_by = request.user.id
                    #             new_calendar.save()

                    #         messages.success(request, 'New fiscal year is started')
                except:
                    state = "Invalid session date"
                    return render_to_response('login.html',
                                              RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                       'company_list': company_list}))

                staff_selected = Staff.objects.filter(is_hidden=0, user_id=user.id, company_id=request.POST.get('company')).first()
                staff_userpermissions = StaffUserPermissions.objects.filter(user_id=user.id)

                if not staff_selected and not user.is_superuser:
                    state = "Your account is not belong to this company, please select the correct company."
                    return render_to_response('login.html',
                                              RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                       'company_list': company_list}))
                else:
                    if staff_selected and staff_selected.is_admin:
                        request.session['staff_admin'] = 1
                    if user.is_active:
                        login(request, user)
                        update_acc_t = threading.Thread(name='update_acc', target=update_account_balance, args=(request,), daemon = False)
                        update_acc_t.start()
                        # update_account_balance(request)
                        company = Company.objects.get(pk=company_id)
                        request.session['use_inventory'] = company.is_inventory
                        request.session['company_name'] = company.name
                        if staff_userpermissions:
                            allowed = []
                            for user_permission in staff_userpermissions:
                                allowed.append(user_permission.permission.codename)
                            request.session['permission_staff'] = allowed
                            if 'all_sp' in allowed:
                                update_order_rate_t = threading.Thread(name='update_order_rate', target=update_order_exchangerate, args=(request,), daemon = True)
                                if company.id not in [1, 2]: # not Mirapro and Muto
                                    update_order_rate_t.start()
                                report_list = Report.objects.filter(is_category=True, is_hidden=False).values_list('id', 'name').order_by('name')
                                request.session['report_list'] = list(report_list)
                                if company.is_inventory:
                                    request.session['stk_report_list'] = ST_REPORT_LIST
                                else:
                                    request.session['stk_report_list'] = []
                                return HttpResponsePermanentRedirect(reverse('page_sp'))
                            elif 'all_acc' in allowed:
                                request.session['report_list'] = []
                                return HttpResponsePermanentRedirect(reverse('page_acc'))
                        else:
                            return HttpResponsePermanentRedirect(reverse('home_load'))

                    else:
                        state = "Your account is not active, please contact the site admin."
                        return render_to_response('login.html', RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                                         'company_list': company_list}))
            else:
                if user.is_superuser:
                    if user.is_active:
                        login(request, user)
                        return HttpResponsePermanentRedirect(reverse('home_load'))
                    else:
                        state = "Your account is not active, please contact the site admin."
                        return render_to_response('login.html', RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                                         'company_list': company_list}))
                else:
                    state = "Please select your compnay!"
                    return render_to_response('login.html',
                                              RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                       'company_list': company_list}))
        else:
            login_count = cache.get(username + 'login_count')
            if not login_count:
                cache.set(username + 'login_count', 0)
            login_count = int(login_count) + 1
            cache.set(username + 'login_count', login_count)

            if login_count >= 3:
                messages_error = "Your username and/or password were incorrect."
                return HttpResponsePermanentRedirect(reverse('reset_confirm'))
            else:
                state = "Your username and/or password were incorrect."
                return render_to_response('login.html', RequestContext(request, {'state': state, 'login_comp': login_comp,
                                                                                 'company_list': company_list}))

    # fsc_year = FiscalCalendar.objects.filter(is_hidden=0).values_list('fiscal_year', flat=True).order_by('fiscal_year').distinct().last()
    # latest_fsc_data = FiscalCalendar.objects.filter(is_hidden=0, fiscal_year=fsc_year)
    # latest_fsc_data = sorted(latest_fsc_data, key=lambda FiscalCalendar: int(FiscalCalendar.period))
    # end_date = latest_fsc_data[-1].end_date.strftime("%Y-%m-%d")

    state = "Please select your company"
    return render_to_response('login.html', RequestContext(request, {'state': state,
                                                                     'company_list': company_list}))


def logout_do(request):
    logout(request)
    request.session['login_company_id'] = ''
    request.session['staff_admin'] = 0
    request.session['use_inventory'] = 0
    company_list = get_company_list(request)
    state = "Please log in below..."
    # fsc_year = FiscalCalendar.objects.filter(is_hidden=0).values_list('fiscal_year', flat=True).order_by('fiscal_year').distinct().last()
    # latest_fsc_data = FiscalCalendar.objects.filter(is_hidden=0, fiscal_year=fsc_year)
    # latest_fsc_data = sorted(latest_fsc_data, key=lambda FiscalCalendar: int(FiscalCalendar.period))
    # end_date = latest_fsc_data[-1].end_date.strftime("%Y-%m-%d")
    return render_to_response('login.html', RequestContext(request, {'state': state, 'company_list': company_list}))


@login_required
def user_profile(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
        if staff.company_id:
            company = Company.objects.get(pk=staff.company_id)
        else:
            company = Company()
        return render_to_response('user-profile.html',
                                  RequestContext(request, {'staff': staff, 'company': company, 'media_url': s.MEDIA_URL}))
    except OSError as e:
        messages.add_message(request, messages.ERROR, e, extra_tags='user_profile')
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist. " \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def image_profile(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company_id).first()
        profile_image = request.FILES.get('profile_image', False)
        if profile_image:
            staff.image.delete(False)
            staff.image.save(profile_image.name, profile_image)
        return HttpResponsePermanentRedirect(reverse('user_profile'))
    except OSError as e:
        messages.add_message(request, messages.ERROR, e, extra_tags='image_profile')


@login_required
def load_user_list(request):
    user_list = User.objects.all()
    return render_to_response('user-list.html', RequestContext(request, {'user_list': user_list}))


@login_required
def load_staff_list(request):

    return render(request, 'staff-list.html')


@login_required
def load_permission_alert(request):
    return render_to_response('permission-alert.html')


@login_required
def load_404_error(request):
    return render_to_response('404.html')


@login_required
def password_change(request):
    user = User.objects.get(pk=request.user.id)
    username = request.user.username
    password = request.POST.get('password_old')

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            check = authenticate(username=username, password=password)
            if check is not None:
                password_new = request.POST.get('password_new')
                password_confirm = request.POST.get('password_confirm')
                check = True
                while check:
                    if len(password_new) < 6 or len(password_new) > 12:
                        form.add_error('password_new', 'Password New must contain 6 to 12 characters!')
                        break
                    elif not re.search("[a-z]", password_new):
                        form.add_error('password_new', 'Password New must contain at least one lowercase letter (a-z)!')
                        break
                    elif not re.search("[0-9]", password_new):
                        form.add_error('password_new', 'Password New must contain at least one number (0-9)!')
                        break
                    elif not re.search("[A-Z]", password_new):
                        form.add_error('password_new', 'Password New must contain at least one uppercase letter (A-Z)!')
                        break
                    else:
                        form.add_error('password_new', 'Password New is correct!')
                        # check = False
                        if password_new == password_confirm:
                            user.set_password(password_new)
                            user.save()
                            form.add_error('password_old', 'Change Password Successfully!')
                            return render(request, 'user-change-password.html', {'form': form})
                        else:
                            form.add_error("password_confirm", "Confirm password is not match with new password ")
                            return render(request, 'user-change-password.html', {'form': form})
                        break
            else:
                form.add_error('password_old', 'Old Password is not correct!')
                return render(request, 'user-change-password.html', {'form': form})
    else:
        form = ChangePasswordForm()
    return render_to_response('user-change-password.html', RequestContext(request, {'user': user, 'form': form}))


def save_multi_company(request, my_staff, my_user):
    company_selected_list = request.POST.getlist('my_company_list')
    if company_selected_list:
        for my_company_select in company_selected_list:
            my_staff_add = Staff.objects.filter(is_hidden=0, user_id=my_staff.user_id, company_id=my_company_select).first()

            if not my_staff_add:
                my_staff_add = Staff()
                my_staff_add.create_date = datetime.datetime.today()
            my_staff_add.phone = request.POST.get('phone')
            my_staff_add.fax = request.POST.get('fax')
            my_staff_add.user = my_user
            my_staff_add.company_id = my_company_select
            my_staff_add.update_date = datetime.datetime.today()
            my_staff_add.update_by = request.user.id
            my_staff_add.is_hidden = 0
            my_staff_add.is_admin = 'chkIsAdmin' in request.POST
            my_staff_add.notifyChangeSP = 'notifyChangeSP' in request.POST
            my_staff_add.save()

            # Save image in staff directory
            file_upload = request.FILES.get('staff_image', False)
            if file_upload:
                my_staff_add.image.delete(False)
                my_staff_add.image.save(file_upload.name, file_upload)

        staff_delete_list = Staff.objects.filter(is_hidden=0, user_id=my_staff.user_id, ) \
            .exclude(company_id__in=company_selected_list)
        if staff_delete_list:
            for staff_delete in staff_delete_list:
                staff_delete.delete()


def save_staff(request, my_staff, my_user):
    my_staff.phone = request.POST.get('phone')
    my_staff.fax = request.POST.get('fax')
    my_staff.user = my_user
    company_id = request.POST.get('company')
    my_staff.company = Company.objects.get(id=company_id)
    my_staff.update_date = datetime.datetime.today()
    my_staff.update_by = request.user.id
    my_staff.is_hidden = 0
    my_staff.is_admin = 'chkIsAdmin' in request.POST
    my_staff.notifyChangeSP = 'notifyChangeSP' in request.POST
    my_staff.save()

    # Save image in staff directory
    file_upload = request.FILES.get('staff_image', False)
    if file_upload:
        my_staff.image.delete(False)
        my_staff.image.save(file_upload.name, file_upload)

    staff_list = Staff.objects.filter(is_hidden=0, user_id=my_user.id)
    if staff_list:
        for o_staff in staff_list:
            o_staff.phone = request.POST.get('phone')
            o_staff.fax = request.POST.get('fax')
            o_staff.update_date = datetime.datetime.today()
            o_staff.update_by = request.user.id
            o_staff.is_hidden = 0
            if request.POST.get('chkIsAdmin'):
                o_staff.is_admin = request.POST.get('chkIsAdmin')
            else:
                o_staff.is_admin = 0
                o_staff.save()

            # Save image in staff directory
            file_upload = request.FILES.get('staff_image', False)
            if file_upload:
                o_staff.image.delete(False)
                o_staff.image.save(file_upload.name, file_upload)


def get_request_checkbox_value(request_value):

    return 0 if request_value == None else 1


def save_user_info(request, my_staff, my_user):
    my_user.id = my_staff.user_id
    my_user.email = request.POST.get('email')
    my_user.first_name = request.POST.get('first_name')
    my_user.last_name = request.POST.get('last_name')
    my_user.is_active = get_request_checkbox_value(request.POST.get('chkIsActive'))
    my_user.is_superuser = get_request_checkbox_value(request.POST.get('chkIsSuperAdmin')) if request.user.is_superuser else 0
    my_user.save()


def save_group_info(request, my_user):
    group_selected_list = request.POST.getlist('my_group_list')

    # But we generate based on the permission set in group
    group_list = Group.objects.filter(id__in=group_selected_list)
    permission_selected_list = []
    for group in group_list:
        permission_selected_list.extend(group.permissions.all().values('id'))

    # permission_selected_list is list of dict, we just need the value in string
    selected_list = []
    for permission in permission_selected_list:
        selected_list.extend([str(permission['id'])])
    # Make the value unique
    permission_selected_list = set(selected_list)

    my_user.groups = group_selected_list
    my_user.user_permissions = permission_selected_list
    my_user.save()

    # Update staff permission
    staff_permission_selected_list = request.POST.getlist('my_permission_list')

    # Delete current permission first
    current_permission_list = StaffUserPermissions.objects.filter(user_id=my_user.id)
    for current_permission in current_permission_list:
        current_permission.delete()

    for staff_permission in staff_permission_selected_list:
        StaffUserPermissions.objects.create(permission_id=staff_permission, user_id=my_user.id)


def get_companylist(request, my_staff):
    staff_list = Staff.objects.filter(is_hidden=0, user_id=my_staff.user_id)
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0

    if request.user.is_superuser:
        company_list = Company.objects.filter(is_hidden=0, is_active=True) \
            .annotate(mSelected=Value(False, output_field=models.BooleanField()))
    else:
        company_list = Company.objects.filter(id=company_id)\
            .annotate(mSelected=Value(False, output_field=models.BooleanField()))
    for my_company in company_list:
        for myStaff in staff_list:
            if myStaff.company_id == my_company.id:
                my_company.mSelected = True

    return company_list


def get_group_permission_list(my_user):
    group_list = Group.objects.all().annotate(mSelected=Value(False, output_field=models.BooleanField()))
    permission_list = StaffPermission.objects.all()
    group_selected_list = my_user.groups.all()
    permission_selected_list = StaffUserPermissions.objects.filter(user_id=my_user.id)

    selected_group = group_list.filter(id__in=group_selected_list)
    for my_group in selected_group:
        my_group.mSelected = True
    group_list = list(chain(selected_group, group_list.exclude(id__in=group_selected_list)))

    selected_permission = permission_list.filter(id__in=permission_selected_list.values('permission'))
    for my_per in selected_permission:
        my_per.mSelected = True
    permission_list = list(chain(selected_permission, permission_list.exclude(id__in=permission_selected_list.values('permission'))))

    return group_list, permission_list


@login_required
@permission_required('staffs.change_staff', login_url='/alert/')
def staff_change_info(request, staff_id):

    # Make sure the default django groups permission is correct
    reassign_group_permission(request)

    my_staff = Staff.objects.get(pk=staff_id)
    my_user = User.objects.get(pk=my_staff.user_id)

    company_list = get_companylist(request, my_staff)
    group_list, permission_list = get_group_permission_list(my_user)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Save user information
                save_user_info(request, my_staff, my_user)

                # Save group information
                save_group_info(request, my_user)

                # check to save multi company
                if request.user.is_superuser:
                    save_multi_company(request, my_staff, my_user)

                else:
                    # Save staff information
                    save_staff(request, my_staff, my_user)

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='staff_add')
        return HttpResponsePermanentRedirect(reverse('staff_list'))

    return render_to_response('staff-edit.html', RequestContext(request,
                                                                {'staff': my_staff,
                                                                 'company_list': company_list,
                                                                 'group_list': group_list,
                                                                 'permission_list': permission_list,
                                                                 'media_root': s.MEDIA_ROOT,
                                                                 'media_url': s.MEDIA_URL, 'staff_url': s.STAFF_ROOT}))


@login_required
@permission_required('staffs.delete_staff', login_url='/alert/')
def staff_delete(request, staff_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                staff = Staff.objects.get(pk=staff_id)
                staff.is_hidden = True
                staff.save()

                my_user = User.objects.get(pk=staff.user_id)
                my_user.is_active = False
                my_user.save()

                return HttpResponsePermanentRedirect(reverse('staff_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='company_delete')


@login_required
@permission_required('staffs.add_staff', login_url='/alert/')
def staff_add(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        user_email = request.POST.get("email")
        user_name = request.POST.get("username")
        user_pass = request.POST.get('password', None)
        user_pass_confirm = request.POST.get('password_confirm', None)
        if form.is_valid():
            if User.objects.filter(username=user_name).exists():
                form.add_error("username", "This username is already in use.")
                return render(request, 'staff-add.html', {'form': form})
            if User.objects.filter(email=user_email).exists():
                form.add_error("email", "This email is already in use.")
                return render(request, 'staff-add.html', {'form': form})
            if user_pass != user_pass_confirm:
                form.add_error("password_confirm", "Confirm password is different password ")
                return render(request, 'staff-add.html', {'form': form})
            if len(user_pass) < 6 or len(user_pass) > 12:
                form.add_error('password', 'Password New must contain 6 to 12 characters!')
                return render(request, 'staff-add.html', {'form': form})
            if not re.search("[a-z]", user_pass):
                form.add_error('password', 'Password New must contain at least one lowercase letter (a-z)!')
                return render(request, 'staff-add.html', {'form': form})
            if not re.search("[0-9]", user_pass):
                form.add_error('password', 'Password New must contain at least one number (0-9)!')
                return render(request, 'staff-add.html', {'form': form})
            if not re.search("[A-Z]", user_pass):
                form.add_error('password', 'Password New must contain at least one uppercase letter (A-Z)!')
                return render(request, 'staff-add.html', {'form': form})

            reassign_group_permission(request)

            with transaction.atomic():
                new_user = User.objects.create_user(user_name, user_email, user_pass)
                new_user.is_active = 1
                new_user.is_staff = 0
                new_user.is_superuser = 0
                new_user.save()

                staff = Staff()
                staff.user = new_user
                staff.phone = ""
                staff.fax = ""
                try:
                    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
                    staff.company_id = company_id
                except ObjectDoesNotExist:
                    pass
                staff.create_date = datetime.datetime.today()
                staff.update_date = datetime.datetime.today()
                staff.update_by = request.user.id
                staff.is_hidden = 0
                staff.is_admin = 0
                staff.save()
            return HttpResponseRedirect(reverse('staff_edit', args=(), kwargs={'staff_id': staff.id}))
    else:
        form = UserForm()
    return render(request, 'staff-add.html', {'form': form})


def reassign_group_permission(request):
    group_list = Group.objects.all().annotate(mSelected=Value(False, output_field=models.BooleanField()))
    permission_list = Permission.objects\
        .exclude(content_type__app_label__contains='admin') \
        .exclude(content_type__model__contains='user') \
        .exclude(content_type__model__contains='permission') \
        .exclude(content_type__app_label__contains='contenttypes') \
        .exclude(content_type__app_label__contains='sessions') \
        .exclude(content_type__model__contains='company') \
        .annotate(mSelected=Value(False, output_field=models.BooleanField()))

    for group in group_list:
        if group.name in "Company Admin":
            permission_selected_list = group.permissions.all()
            permission_not_selected_list = permission_list.exclude(id__in=permission_selected_list)

        elif group.name in "Staff_Acc":
            permission_selected_list = group.permissions.all()
            #orders, items, inventory, locations
            accounting_permission_list = permission_list\
                .exclude(content_type__app_label__contains='orders')\
                .exclude(content_type__app_label__contains='items')\
                .exclude(content_type__app_label__contains='inventory')\
                .exclude(content_type__app_label__contains='locations')
            permission_not_selected_list = accounting_permission_list.exclude(id__in=permission_selected_list)

        elif group.name in "Staff_SP":
            permission_selected_list = group.permissions.all()
            # accounts, accounting, and transactions
            accounting_permission_list = permission_list\
                .exclude(content_type__app_label__contains='accounts')
            # SP needs to do closing and data will move to accounting so we need to allow it to access accounting and transactions
            permission_not_selected_list = accounting_permission_list.exclude(id__in=permission_selected_list)

        for permission in permission_not_selected_list:
            group.permissions.add(permission)


@login_required
def load_group_list(request):
    group_list = Group.objects.all()
    return render_to_response('group-list.html', RequestContext(request, {'group_list': group_list}))


@login_required
@permission_required('auth.add_group', login_url='/alert/')
def group_add(request):
    group = Group()
    form = GroupForm()
    permission_list = StaffPermission.objects.all()
    if request.method == "POST":
        form = GroupForm(request.POST)
        permission_selected_list = request.POST.getlist('my_permission_list')
        group.name = request.POST.get("name")
        if form.is_valid():
            if Group.objects.filter(name=group.name).exists():

                selected_permission = permission_list.filter(id__in=permission_selected_list.values('permission'))
                for my_per in selected_permission:
                    my_per.mSelected = True
                permission_list = list(chain(selected_permission, permission_list.exclude(id__in=permission_selected_list.values('permission'))))

                form.add_error("name", "This group name is already in use.")
                return render(request, 'group-add.html', {'permission_list': permission_list, 'form': form,
                                                          'permission_selected_list': permission_selected_list})
            else:
                with transaction.atomic():
                    group.save()
                    for staff_permission in permission_selected_list:
                        StaffGroupPermissions.objects.create(permission_id=staff_permission, group_id=group_id)
                    return HttpResponsePermanentRedirect(reverse('load_group_list'))
    return render(request, 'group-add.html',
                  context_instance=RequestContext(request, {'permission_list': permission_list, 'form': form}))


@login_required
@permission_required('auth.change_group', login_url='/alert/')
def group_edit(request, group_id):
    group = Group.objects.get(id=group_id)
    permission_list = StaffPermission.objects.all()
    permission_selected_list = StaffGroupPermissions.objects.filter(group_id=group_id)

    selected_permission = permission_list.filter(id__in=permission_selected_list.values('permission'))
    for my_per in selected_permission:
        my_per.mSelected = True
    permission_list = list(chain(selected_permission, permission_list.exclude(id__in=permission_selected_list.values('permission'))))

    if request.method == "POST":
        with transaction.atomic():
            group.id = group_id
            group.name = request.POST.get("group_name")

            # Update staff permission
            staff_permission_selected_list = request.POST.getlist('my_permission_list')

            # Delete current permission first
            current_permission_list = StaffGroupPermissions.objects.filter(group_id=group_id)
            for current_permission in current_permission_list:
                current_permission.delete()

            for staff_permission in staff_permission_selected_list:
                StaffGroupPermissions.objects.create(permission_id=staff_permission, group_id=group_id)

            group.save()

            return HttpResponsePermanentRedirect(reverse('load_group_list'))
    else:
        return render(request, 'group-edit.html',
                      context_instance=RequestContext(request, {'group': group, 'permission_list': permission_list}))


@login_required
@permission_required('auth.delete_group', login_url='/alert/')
def group_delete(request, group_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                group = Group.objects.get(pk=group_id)
                group.delete()
                return HttpResponsePermanentRedirect(reverse('load_group_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='group_delete')


@login_required
def home_load(request):

    try:
        if 'all_sp' in request.session['permission_staff']:
            return redirect('/orders/landing_sp/')
        elif 'all_acc' in request.session['permission_staff']:
            return redirect('/accounting/landing_acc/')
    except Exception as e:
        pass

    return render_to_response('home.html', RequestContext(request))


def reset_password(request, user_name, old_password):
    if request.method == 'POST':
        user = User.objects.filter(username=user_name,
                                   password=urlsafe_base64_decode(force_bytes(old_password))).first()
        if user is not None:
            password_new = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            u = User.objects.get(username=user_name)
            check = True
            while check:
                if len(password_new) < 6 or len(password_new) > 12:
                    state = "Password New must contain 6 to 12 characters!"
                    break
                elif not re.search("[a-z]", password_new):
                    state = "Password New must contain at least one lowercase letter (a-z)!"
                    break
                elif not re.search("[0-9]", password_new):
                    state = "Password New must contain at least one number (0-9)!"
                    break
                elif not re.search("[A-Z]", password_new):
                    state = "Password New must contain at least one uppercase letter (A-Z)!"
                    break
                else:
                    if password_new == password_confirm:
                        u.set_password(password_new)
                        u.save()
                        state = "Password changed successful."
                        return render_to_response('reset-password-alert.html',
                                                  RequestContext(request, {'state': state}))
                    else:
                        state = "Confirm password is not match with new password."
                        return render_to_response('reset-password.html',
                                                  RequestContext(request, {'state': state,
                                                                           'user_name': user_name,
                                                                           'old_password': old_password
                                                                           }))
                    break
            return render_to_response('reset-password.html', RequestContext(request, {'state': state,
                                                                                      'user_name': user_name,
                                                                                      'old_password': old_password
                                                                                      }))
    return render_to_response('reset-password.html', RequestContext(request, {'user_name': user_name,
                                                                              'old_password': old_password}))


def reset_confirm(request):
    if request.method == 'POST':
        try:
            my_input = request.POST.get("email")
            my_user_list = User.objects.filter(username__contains=my_input) | User.objects.filter(
                email__contains=my_input)

            if my_user_list:
                my_user = my_user_list.first()
                my_url = HttpResponseRedirect(reverse('reset_password', args=(),
                                                      kwargs={'user_name': my_user.username,
                                                              'old_password': urlsafe_base64_encode(
                                                                  force_bytes(my_user.password))}))
                my_link = s.ABSOLUTEURI_PROTOCOL + request.get_host() + my_url.url
                if my_user.email:
                    email = EmailMessage('reset-password-mail.html',
                                         {'username': my_user.username,
                                          'email': my_user.email,
                                          'link': my_link},
                                         s.DEFAULT_FROM_EMAIL,
                                         to=[my_user.email])
                    email.send()
            else:
                messages.add_message(request, messages.ERROR, "Your user name / e-mail address does not exist.",
                                     extra_tags='reset_confirm')
                return render_to_response('reset_password_confirm.html', RequestContext(request))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='reset_confirm')
        state = "Reset e-mail had sent. Please check your e-mail."
        return render_to_response('reset-password-alert.html', RequestContext(request, {'state': state}))
    return render_to_response('reset_password_confirm.html', RequestContext(request))


@login_required
def Staff__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = Staff.objects.filter(is_hidden=0)
    if not request.user.is_superuser:
        list_filter = list_filter.filter(company_id=company_id)
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(update_date__contains=search)
                                         | Q(user__username__contains=search)
                                         | Q(user__last_name__contains=search)
                                         | Q(user__first_name__contains=search)
                                         | Q(user__email__contains=search)
                                         | Q(company__name__contains=search)
                                         )

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "user__username"
    elif order_column == "2":
        column_name = "user__first_name"
    elif order_column == "3":
        column_name = "user__last_name"
    elif order_column == "4":
        column_name = "user__email"
    elif order_column == "5":
        column_name = "company__name"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%Y-%m-%d"),
                "user__username": field.user.username,
                "user__first_name": field.user.first_name,
                "user__last_name": field.user.last_name,
                "user__email": field.user.email,
                "company__name": field.company.name,
                "is_active": str(field.user.is_active),
                "is_admin": str(field.is_admin),
                "is_superuser": str(field.user.is_superuser)}
        array.append(data)

    if request.user.is_superuser:
        records_total = Staff.objects.filter(is_hidden=0).count()
    else:
        records_total = Staff.objects.filter(is_hidden=0, company_id=company_id).count()
    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def Group_list__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Group.objects.all()
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(name__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "name"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for j, field in enumerate(list):
        data = {"id": field.id,
                "name": field.name}
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')



def update_account_balance(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    session_date = request.session['session_date']
    fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0,
                            start_date__lte=session_date,
                            end_date__gte=session_date).first()
    if fsc_calendar:
        s_year = fsc_calendar.fiscal_year
        s_period = fsc_calendar.period
    else:
        s_year = session_date.year
        s_period = session_date.month

    try:
        journal = Journal.objects.filter(is_hidden=False, company_id=company.id,
                                        journal_type=dict(TRANSACTION_TYPES)['GL'],
                                        status=int(STATUS_TYPE_DICT['Posted']),
                                        error_entry=0,
                                        ).order_by('-perd_year', '-perd_month').first()
        if journal:
            if (int(s_year) > int(journal.perd_year)) or \
                (int(s_year) == int(journal.perd_year) and int(s_period) > journal.perd_month):
                    result = carry_forward_balance(request, journal.perd_month-1, journal.perd_year)
    except Exception as e:
        print(e)


    return True


def carry_forward_balance(request, from_month, from_year):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    history_list = AccountHistory.objects.filter(is_hidden=False, company_id=company.id,
                                                account__is_hidden=False, account__company_id=company.id,
                                                period_month=from_month, period_year=from_year)\
                        .exclude(source_currency_id__isnull=True)\
                        .select_related('account', 'source_currency')
                        # .exclude(Q(source_net_change=0) & Q(functional_net_change=0))\
                        # .exclude(account__account_type=int(ACCOUNT_TYPE_DICT['Income Statement']))\

    for account_history in history_list:
        src_eb = account_history.source_end_balance
        func_eb = account_history.functional_end_balance
        for i in range(from_month + 1, 13):
            try:
                next_history = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month=i, period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
                    .exclude(source_currency_id__isnull=True)\
                    .first()

                next_history.source_begin_balance = src_eb
                next_history.source_end_balance = round_number(
                    next_history.source_begin_balance) + round_number(next_history.source_net_change)
                next_history.functional_begin_balance = func_eb
                next_history.functional_end_balance = round_number(
                    next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                next_history.save()
                src_eb = next_history.source_end_balance
                func_eb = next_history.functional_end_balance
            except ObjectDoesNotExist as e:
                print(e)

        period_ADJ = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month__in=['ADJ'],
                                                                period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
            .exclude(source_currency_id__isnull=True)

        for ADJ_CLS in period_ADJ:
            ADJ_CLS.source_begin_balance = src_eb
            ADJ_CLS.source_end_balance = round_number(
                ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
            ADJ_CLS.functional_begin_balance = func_eb
            ADJ_CLS.functional_end_balance = round_number(
                ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
            ADJ_CLS.save()

        period_CLS = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month__in=['CLS'],
                                                                period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
            .exclude(source_currency_id__isnull=True)

        for ADJ_CLS in period_CLS:
            ADJ_CLS.source_begin_balance = src_eb
            ADJ_CLS.source_end_balance = round_number(
                ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
            ADJ_CLS.functional_begin_balance = func_eb
            ADJ_CLS.functional_end_balance = round_number(
                ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
            ADJ_CLS.save()
            src_eb = ADJ_CLS.source_end_balance
            func_eb = ADJ_CLS.functional_end_balance


        for year in range(int(from_year) + 1, int(from_year) + 2):
            last_day = None
            for i in range(12):
                _, num_days = calendar.monthrange(year, i + 1)
                last_day = datetime.date(year, i + 1, num_days)
                try:
                    next_history = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                    is_hidden=False,
                                                                    company_id=company.id,
                                                                    account_id=account_history.account_id,
                                                                    period_month=i + 1,
                                                                    period_year=year,
                                                                    source_currency_id=account_history.source_currency_id)\
                        .exclude(source_currency_id__isnull=True)\
                        .first()

                    next_history.source_begin_balance = src_eb
                    next_history.source_end_balance = round_number(
                        next_history.source_begin_balance) + round_number(next_history.source_net_change)
                    next_history.functional_begin_balance = func_eb
                    next_history.functional_end_balance = round_number(
                        next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                    next_history.save()
                    src_eb = next_history.source_end_balance
                    func_eb = next_history.functional_end_balance
                except Exception as e:
                    print(e)
                    period = i + 1
                    create_account_history(request, year, period, last_day, account_history.account_id,
                                            account_history.source_currency_id,
                                            src_eb, company.currency_id,
                                            func_eb)

            period_ADJO = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                            is_hidden=False,
                                                            company_id=company.id,
                                                            account_id=account_history.account_id,
                                                            period_month__in=['ADJ'],
                                                            period_year=year,
                                                            source_currency_id=account_history.source_currency_id)\
                .exclude(source_currency_id__isnull=True)
            if period_ADJO:
                for ADJ_CLS in period_ADJO:
                    ADJ_CLS.source_begin_balance = src_eb
                    ADJ_CLS.source_end_balance = round_number(
                        ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                    ADJ_CLS.functional_begin_balance = func_eb
                    ADJ_CLS.functional_end_balance = round_number(
                        ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                    ADJ_CLS.save()
            else:
                create_account_history(request, year, 'ADJ', last_day, account_history.account_id,
                                        account_history.source_currency_id, src_eb,
                                        company.currency_id, func_eb)

            period_CLSO = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                            is_hidden=False,
                                                            company_id=company.id,
                                                            account_id=account_history.account_id,
                                                            period_month__in=['CLS'],
                                                            period_year=year,
                                                            source_currency_id=account_history.source_currency_id)\
                .exclude(source_currency_id__isnull=True)
            if period_CLSO:
                for ADJ_CLS in period_CLSO:
                    ADJ_CLS.source_begin_balance = src_eb
                    ADJ_CLS.source_end_balance = round_number(
                        ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                    ADJ_CLS.functional_begin_balance = func_eb
                    ADJ_CLS.functional_end_balance = round_number(
                        ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                    ADJ_CLS.save()
                    src_eb = ADJ_CLS.source_end_balance
                    func_eb = ADJ_CLS.functional_end_balance
            else:
                create_account_history(request, year, 'CLS', last_day, account_history.account_id,
                                        account_history.source_currency_id, src_eb,
                                        company.currency_id, func_eb)

    return True



def create_account_history(request, year, period, last_day, account_id, source_currency_id, source_net_change,
                           functional_currency_id, func_net_change):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        account_history = AccountHistory()
        account_history.period_year = year
        account_history.period_month = period
        account_history.period_date = last_day
        account_history.company_id = company_id
        account_history.account_id = account_id
        account_history.source_currency_id = source_currency_id
        account_history.source_begin_balance = source_net_change
        account_history.source_net_change = 0
        account_history.source_end_balance = account_history.source_begin_balance + account_history.source_net_change
        account_history.functional_currency_id = functional_currency_id
        account_history.functional_begin_balance = func_net_change
        account_history.functional_net_change = 0
        account_history.functional_end_balance = account_history.functional_begin_balance + account_history.functional_net_change
        account_history.update_by = request.user.id
        account_history.create_date = datetime.datetime.today()
        account_history.save()
        return True
    except Exception as e:
        print(e)
        return False


def update_order_exchangerate(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    try:
        unapplied_rates = ExchangeRate.objects.filter(company_id=company_id, is_hidden=False,
                                                    apply_flag=False, to_currency_id=company.currency.id)
        for exchangerate in unapplied_rates:
            order_list = Order.objects.filter(is_hidden=False, company_id=company_id, currency_id=exchangerate.from_currency_id,
                                            document_date__year=exchangerate.exchange_date.year, document_date__month=exchangerate.exchange_date.month)
            for order in order_list:
                if order.exchange_rate:
                    order.exchange_rate = exchangerate.rate
                if order.supllier_exchange_rate:
                    order.supllier_exchange_rate = exchangerate.rate
                if order.tax_exchange_rate:
                    order.tax_exchange_rate = exchangerate.rate
                order.save()

            # reset apply flag
            exchangerate.apply_flag = True
            exchangerate.save()

    except Exception as e:
        print(e)
