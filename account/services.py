import ghasedak_sms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def send_otp_sms(phone_number, code):
    if not settings.GHASEDAK_API_KEY:
        if settings.DEBUG:
            print(f'[DEV ONLY] OTP for {phone_number}: {code}')
            return
        raise ImproperlyConfigured('GHASEDAK_API_KEY is not set')

    sms = ghasedak_sms.Ghasedak(settings.GHASEDAK_API_KEY, settings.GHASEDAK_SENDER)
    sms.send_single_sms(
        ghasedak_sms.SendSingleSmsInput(
            message=str(code),
            receptor=phone_number,
            line_number=settings.GHASEDAK_LINE_NUMBER,
            send_date='',
            client_reference_id='',
        )
    )