from random import randint
import jwt
from .configuration import expiry_time_of_token
from datetime import datetime, timedelta, timezone

#otp_util() will return 6 digit random integer number

# this function creates jwt tokens -session
def create_token(user_id):
    # print('user_id: {}'.format(user_id))
    payload = {
                    'user_id': user_id,
                    # 'exp': datetime.now() + timedelta(seconds=60)
    }
    jwt_token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')
    # print ('jwt_token: {}'.format(jwt_token))
    return jwt_token
# create_token(309651)
#function for decoding the jwt token 
def decode_token(token):
    token = jwt.decode(token, 'secret', algorithms=['HS256'])
    return token


def is_valid_token(token):
    try:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{time}] - token - {token} - size {len(token.encode('utf-8'))} .....")

        token = jwt.decode(token, 'secret', algorithms=['HS256'])

        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{time}] - token decoded successfylly {token} .....")

        user_id = token.get('user_id')

        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{time}] - user id found for token {user_id} .....")

        user_data = get_if_exists(User,id=user_id)

        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{time}] - user data extracted {user_data} .....")

        if user_data:
            return user_id
        else:
            return False
    except Exception as e:
        return False


def get_object_or_none(klass, *args, **kwargs):
    queryset = klass._default_manager.all() if hasattr(klass, '_default_manager') else klass
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        # raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
        return None


def build_response(success=True, data=None, message=None):
    return Response(data={'status': success, 'data': data, 'message': message})
    
def get_if_exists(model, **kwargs):
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:  # Be explicit about exceptions
        obj = None
    return obj


