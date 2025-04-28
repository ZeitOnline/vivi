import ssl


def create_context_without_strict():
    context = ssl._old_create_default_context()
    # Use looser `DEFAULT` instead of `VERIFY_X509_STRICT | VERIFY_X509_PARTIAL_CHAIN`
    context.verify_flags = ssl.VERIFY_DEFAULT
    return context
