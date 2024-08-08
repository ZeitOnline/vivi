from sqlalchemy import Boolean, Column, Unicode


class CommonMetadata:
    access = Column(Unicode, index=True, info={'namespace': 'document', 'name': 'access'})
    overscrolling = Column(
        Boolean, index=True, info={'namespace': 'document', 'name': 'overscrolling'}
    )
