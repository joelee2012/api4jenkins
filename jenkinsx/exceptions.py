# encoding: utf-8


class ItemNotFoundError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class ItemExistsError(Exception):
    pass


class UnsafeCharacterError(Exception):
    pass


class BadRequestError(Exception):
    pass


class ServerError(Exception):
    pass
