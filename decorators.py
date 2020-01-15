from functools import wraps


def sign_exempt(view_func):
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.sign_exempt = True
    return wraps(view_func)(wrapped_view)


def jwt_exempt(view_func):
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.jwt_exempt = True
    return wraps(view_func)(wrapped_view)
