import random


def generate_otp():
    """
    Generate OTP 5 digit.
    Contoh:
    48392
    """

    return str(
        random.randint(
            10000,
            99999
        )
    )