import hashlib
import json
import uuid
import time

from ..models import StudentAccount, TeacherAccount
from ..util import Util
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage


@csrf_exempt
def register_check(req):
    if req.method == 'GET':
        token = req.GET.get('query', '')
        print(token)
        account = get_account(req.GET.get('type', ''), token, 2)
        if account is not None:
            account.token = get_token(account.password.split(":")[0])
            account.level = 1
            account.save()
            return Util.create_response(u"<h1>인증을 완료하였습니다. 창을 닫아주세요.</h1>")
    return Util.create_response(u"<h1>잘못된 접근</h1>")


@csrf_exempt
def register(req):
    if req.method == 'POST':
        uid = uuid.uuid4()
        print(req.body.decode("utf-8"))
        json_data = json.loads(req.body.decode("utf-8"))
        account = get_account(json_data['type'], json_data['email'], 1)
        if account is not None:
            account.password = uid.__str__() + ":" + get_sha512(uid.__str__() + json_data['password'])
            account.student_number = json_data['stnumber']
            account.name = json_data['name']
            account.token = register_email(json_data['email'], get_token(uid.urn.__str__()), json_data['name'], json_data['type'])
            account.save()
            return Util.create_response('register_success')
        return Util.create_response({'response': 'register_failed:existent_account'})
    return Util.create_response(u"<h1>잘못된 접근</h1>")


@csrf_exempt
def login(req):
    if req.method == 'POST':
        json_data = json.loads(req.body.decode("utf-8"))
        account = get_account(json_data['type'], json_data['email'])
        if account is not None:
            print(account.password.split(":")[0])
            if 'token' in json_data:
                if not json_data['token'] == account.token:
                    return Util.create_response({'response': 'login_failed:token'})
            elif not account.password == (account.password.spliget_sha512t(":")[0] + json_data['password']):
                return Util.create_response({'response': 'login_failed:password'})
            return Util.create_response({'response': 'login_success', 'token': get_token(account.password.split(":")[0])})
        return Util.create_response({'response': 'login_failed:Nonexistent'})
    return Util.create_response(u"<h1>잘못된 접근</h1>")


def get_account(acoount_type, email, flag=0):
    acoount_type = StudentAccount if acoount_type == "st" else TeacherAccount if acoount_type == "tch" else None
    if acoount_type is None:
        return None
    o = acoount_type.objects
    return o.get(token=email) if flag == 2 else o.create(email=email) if flag == 1 else o.get(email=email) if o.filter(email=email).exists() else None


def get_sha512(input_string):
    return hashlib.sha3_512(input_string.encode('utf-8')).hexdigest()


def get_token(uid):
    return get_sha512(uid + ':' + (time.time() * 1000).__int__().__str__())


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
