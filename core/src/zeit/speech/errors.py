class AudioReferenceError(Exception):
    """
    An exception raised if the article was updated after publish, to avoid publishing it with
    unreviewed changes
    """
