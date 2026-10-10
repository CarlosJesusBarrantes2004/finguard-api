from rest_framework.throttling import UserRateThrottle


class TransferenciaRateThrottle(UserRateThrottle):
    scope = "transferencias_limite"
