
class JenkinsAPIException(Exception):
    pass


class ItemNotFoundError(JenkinsAPIException):
    pass


class AuthenticationError(JenkinsAPIException):
    pass


class ItemExistsError(JenkinsAPIException):
    pass


class UnsafeCharacterError(JenkinsAPIException):
    pass


class BadRequestError(JenkinsAPIException):
    pass


class ServerError(JenkinsAPIException):
    pass
