from sqlalchemy import Column, Unicode


class CommonMetadata:
    access = Column(Unicode, index=True, info={'namespace': 'document', 'name': 'access'})
