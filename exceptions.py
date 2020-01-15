from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        status_code = response.status_code
        if status_code == 404:
            return AESJsonResponse(status=404, msg='未找到')

    return response