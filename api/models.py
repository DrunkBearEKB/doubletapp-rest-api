import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, BYTEA


db = SQLAlchemy()


class PetModel(db.Model):
    __tablename__ = 'pet_table'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String())
    age = db.Column(db.Integer())
    type = db.Column(db.String())
    photos = db.Column(db.String())
    created_at = db.Column(db.String())

    def __init__(self, name, age, type, created_at):
        self.name = name
        self.age = age
        self.type = type
        self.photos = ''
        self.created_at = created_at

    def __repr__(self):
        return f'PetModel(' \
               f'id={self.uuid}; ' \
               f'name={self.name}; ' \
               f'age={self.age}; ' \
               f'type={self.type}; ' \
               f'photos={self.photos}; ' \
               f'created_at={self.created_at};)'


class PhotoModel(db.Model):
    __tablename__ = 'photo_table'

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extension = db.Column(db.String())
    content_type = db.Column(db.String())
    binary = db.Column(BYTEA)

    def __init__(self, extension, content_type, binary):
        self.extension = extension
        self.content_type = content_type
        self.binary = binary

    def __repr__(self):
        return f'PhotoModel(' \
               f'extension={self.extension}; ' \
               f'content_type={self.content_type}; ' \
               f'binary={self.binary};)'
