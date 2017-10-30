from django.http import HttpResponse
from pyfcm import FCMNotification
import hashlib
import time
from server.models import TeacherAccount, StudentAccount
from django.core.mail import EmailMessage


def create_response(msg):
    return HttpResponse(content=msg, charset='utf-8')


def send_fcm(to, title, msg, data):
    push_service = FCMNotification(
        api_key="AAAAycRHOh8:APA91bGxatLE_w6SojzWQiLtdSioOTDu5qXRSGNw6QZ1X2CXpVoJr7qx5YfYCetD2nISWziAwyqSs9AKxBQ8A2zCxOQUxjpuT4JKLqNc0svrSKIo2VMgWhcppAPepgUvNJcF9brYwVoOg")
    push_service.notify_single_device(registration_id=to, message_title=title, message_body=msg, data_message=data)


def get_account(acoount_type, email, flag=False):
    acoount_type = StudentAccount if acoount_type == "st" else TeacherAccount if acoount_type == "tch" else None
    if acoount_type is None:
        return None
    o = acoount_type.objects
    return o.get(token=email) if flag else o.get(email=email) if o.filter(email=email).exists() else None


def get_sha512(input_string):
    return hashlib.sha3_512(input_string.encode('utf-8')).hexdigest()


def get_token(uid):
    return get_sha512(uid + ':' + (time.time() * 1000).__int__().__str__())


def is_login(req):
    if not req.session.get('token', False):
        return 3
    account = get_account(TeacherAccount, req.session.get('token'), True)
    if account is None:
        return 3
    elif account.level == 0:
        return 2
    account.token = get_token(account.password.split(":")[0])
    req.session['token'] = account.token
    return 1


def register_email(email, token, name, t):
    msg = EmailMessage(
        'School Notification Service 이메일 인증 메일',
        '<h2>가입을 시도한 적이 없다면 누르지 마시기 바랍니다.</h2>안녕하세요, ' + name + '님<br>회원가입을 완료하기 위해 아래의 링크를 클릭하세요.<br><a '
                                                                'href="http://jaeheon.com:8000/email?query=' + token + '&type=' + t + '">인증하기</a>',
        'schoolnotificationserviceu@gmail.com', [email]
    )
    msg.content_subtype = "html"
    msg.send()
    return token


def send_fcm_data(to, data):
    push_service = FCMNotification(
        api_key="AAAAycRHOh8:APA91bGxatLE_w6SojzWQiLtdSioOTDu5qXRSGNw6QZ1X2CXpVoJr7qx5YfYCetD2nISWziAwyqSs9AKxBQ8A2zCxOQUxjpuT4JKLqNc0svrSKIo2VMgWhcppAPepgUvNJcF9brYwVoOg")
    push_service.single_device_data_message(registration_id=to, data_message=data)
