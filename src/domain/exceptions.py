# exceptions.py

class DomainException(Exception):
    """
    Basisklasse für fachliche Fehler in der Domain.
    """
    pass

class OpsGenieApiException(Exception):
    pass


class OpsGenieAuthException(OpsGenieApiException):
    pass


class OpsGenieNotFoundException(OpsGenieApiException):
    pass


class OpsGenieConnectionException(OpsGenieApiException):
    pass