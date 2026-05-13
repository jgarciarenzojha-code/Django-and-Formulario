from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class EmpleadoRateThrottle(UserRateThrottle):
    scope = 'empleado'


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'
