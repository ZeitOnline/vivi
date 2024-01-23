class RetryException(Exception):
    """An exception raised for errors that should trigger a retry for the task."""


class ChecksumMismatchError(Exception):
    """An exception raised when the checksum of the article and the speech do not match."""
