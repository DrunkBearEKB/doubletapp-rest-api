import os
import sys
import uuid
from datetime import datetime

from flask import Flask, request, abort, make_response
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
import flask.scaffold
flask.helpers._endpoint_from_view_func = \
    flask.scaffold._endpoint_from_view_func
from flask_restplus import Api, Resource, fields, reqparse
from flask_migrate import Migrate
from configparser import ConfigParser, ParsingError

from models import db, PetModel, PhotoModel


FILE_CONFIG_NAME = 'config.ini'
PATH_CONFIG_FILE = os.path.dirname(__file__) + '\\' + FILE_CONFIG_NAME
DEFAULT_CONFIG_VALUES = '''[Settings]
api_key = 830s9R7fo8Ew704nz03xBCf489mZ3mx8Dsf23DNo
secure_photos = no
    
[Settings.db]
username = postgres
password = 18723654
address = localhost
port = 5432
name = pets
'''


config = ConfigParser()
if not os.path.exists(PATH_CONFIG_FILE):
    with open(PATH_CONFIG_FILE, mode='w') as file:
        file.write(DEFAULT_CONFIG_VALUES)
try:
    config.read(PATH_CONFIG_FILE)
except ParsingError:
    print(f'Сan not parse the config file, please check its correctness:\n'
          f'{PATH_CONFIG_FILE}')
    sys.exit()

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://' \
    f'{config["Settings.db"]["username"]}:' \
    f'{config["Settings.db"]["password"]}@' \
    f'{config["Settings.db"]["address"]}:' \
    f'{config["Settings.db"]["port"]}/' \
    f'{config["Settings.db"]["name"]}'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(flask_app)
migrate = Migrate(flask_app, db)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(
    app=flask_app,
    version='1.0',
    title='Pets REST API',
    description='Author: Ivanenko Grigoriy',
    authorizations=authorizations, security='apikey'
)
pet_namespace = api.namespace('pets')

# parser for GET pets
parser_get_pets_request = api.parser()
parser_get_pets_request.add_argument('limit', type=int,
                                     help='limit')
parser_get_pets_request.add_argument('offset', type=int,
                                     help='offset')
parser_get_pets_request.add_argument('has_photos', type=bool,
                                     help='has_photos')

# model for POST pet
model_post_pet_response = pet_namespace.model(
    'pet_data_request',
    {
        'name': fields.String(description='pet\'s name', required=True),
        'age': fields.Integer(description='pet\'s age', required=True),
        'type': fields.String(description='pet\'s type', required=True)
    },
)

# parser for DELETE pet
parser_delete_pet_request = api.parser()
parser_delete_pet_request.add_argument('ids', action='append', location='json',
                                       help='ID\'s of pets')

# parser for POST pet's image
parser_post_image_request = reqparse.RequestParser()
parser_post_image_request.add_argument(
    'image', type=werkzeug.datastructures.FileStorage, location='files',
    required=True, help='image'
)


def check_api_key(func):
    def func_wrapped(*args, **kwargs):
        if 'PetPhotoGetResource.get' in str(func) and \
                config['Settings']['secure_photos'] == 'no':
            return func(*args, **kwargs)
        elif 'X-Api-Key' in request.headers.keys() and \
                request.headers['X-Api-Key'] == config['Settings']['api_key']:
            return func(*args, **kwargs)
        else:
            abort(401)

    return func_wrapped


def pet_to_dict(pet) -> dict:
    photos = pet.photos.split(';') if pet.photos != '' else list()

    for i, id_photo in enumerate(photos):
        photo = PhotoModel.query.get_or_404(id_photo)
        photos[i] = {
            'id': id_photo,
            'url': f'{api.base_url}pets/{pet.uuid}/photo/'
                   f'{photo.uuid}'
        }

    return {
        'id': str(pet.uuid),
        'name': pet.name,
        'age': pet.age,
        'type': pet.type,
        'photos': photos,
        'created_at': pet.created_at
    }


def photo_to_dict(photo, pet_id) -> dict:
    return {
        'id': str(photo.uuid),
        'url': f'{api.base_url}pets/{pet_id}/photo/'
               f'{photo.uuid}'
    }


# Можно заметить, что я отклонился от условия задания в том плане, что для
# получения фотографии питомца требуется ID той самой фотографии,
# а не имя файла, но если честно, то кроме как через костыль
# (сделать ещё одну модель, которая по сути своей будет просто словарём,
# в котором каждому имени файла будет сопостовляться ID, и при обращении я
# бы проверял наличие фотографии с таким названием у пользователя, и если
# бы такая находилась, то пользуюясь тим 'словарём' сопостовлял названию
# файла ID фотографии, а по нему уже находил саму фотографию и возвращал).
# Но мне показалось, что использование методики: замена
# <название файла>.<расширение> на <ID фотографии>.<расширение> будет более
# безопасной для клиента, то есть если например у пользователя в названии
# вдруг присутствует какой-то адресс или иная личная информация, то эта
# информация будет скрыта от других, что, вроде бы, хорошо. Я понимаю,
# что это меня не особо оправдывает в том плане, что я не сделал это, но,
# как мне кажется, стоит во всём искать хорошее :)


@pet_namespace.route('/')
class PetResource(Resource):
    @pet_namespace.expect(parser_get_pets_request)
    @check_api_key
    def get(self):
        try:
            limit = request.args.get('limit') \
                if request.args.get('limit') is not None else 20
            limit = int(limit)

            offset = request.args.get('offset') \
                if request.args.get('offset') is not None else 0
            offset = int(offset)

            if request.args.get('has_photos') is None:
                has_photos = None
            elif request.args.get('has_photos') == 'true':
                has_photos = True
            elif request.args.get('has_photos') == 'false':
                has_photos = False
            else:
                abort(400)
                return

        except ValueError:
            abort(400)
            return

        items = PetModel.query.all()
        if has_photos is None:
            pets = list(map(pet_to_dict, items[offset:offset + limit]))
        else:
            pets = []
            i = offset
            while i < len(items) and len(pets) < limit:
                pet = items[i]
                if (has_photos and pet.photos != '') or \
                        (not has_photos and pet.photos == ''):
                    pets.append(pet_to_dict(pet))
                i += 1

        return {
            'count': len(pets),
            'items': pets
        }

    @pet_namespace.expect(model_post_pet_response)
    @check_api_key
    def post(self):
        time_created = str(datetime.now().isoformat(sep='T'))
        time_created = time_created[:time_created.rindex('.')]

        try:
            _type = request.json['type'].lower()
            if _type not in ['dog', 'cat']:
                abort(400)
                return

            pet = PetModel(
                name=request.json['name'],
                age=request.json['age'],
                type=_type,
                created_at=time_created
            )
        except KeyError:
            abort(400)
            return

        db.session.add(pet)
        db.session.commit()

        return pet_to_dict(pet)

    @pet_namespace.expect(parser_delete_pet_request)
    @check_api_key
    def delete(self):
        try:
            ids = request.json['ids']
        except TypeError:
            ids = request.json
        except KeyError:
            abort(400)
            return

        amount_deleted = 0
        errors = []
        for pet_id in ids:
            try:
                uuid.UUID(pet_id, version=4)
            except ValueError:
                errors.append({
                    'id': pet_id,
                    'error': 'Pet with the matching ID was not found.'
                    # хотя лучше бы наверно здесь возвращать другой текст,
                    # например: Invalid format for the pet's ID
                })
                continue

            pet = PetModel.query.get(pet_id)
            if pet is not None:
                db.session.delete(pet)
                db.session.commit()
                amount_deleted += 1
            else:
                errors.append({
                    'id': pet_id,
                    'error': 'Pet with the matching ID was not found.'
                })

        return {
            'deleted': amount_deleted,
            'errors': errors
        }


@pet_namespace.route('/<string:id>/photo')
class PetPhotoPostResource(Resource):
    @pet_namespace.expect(parser_post_image_request)
    @check_api_key
    def post(self, id):
        pet = PetModel.query.get_or_404(id)

        try:
            file_name = request.files.getlist('image')[0].filename
            extension = file_name[file_name.rindex('.') + 1:] \
                if '.' in file_name else file_name
            photo = PhotoModel(
                extension=extension,
                content_type=request.files.getlist('image')[0].content_type,
                binary=request.files.getlist('image')[0].stream.read()
            )
        except IndexError:
            abort(400)
            return

        db.session.add(photo)
        db.session.commit()

        # Если честно, то я особо не знаю как лучше всего хранить файлы в БД,
        # хотя как мне кажется подход в плане хранения всех файлов, например в
        # какой-то папке (организовать там структуру для хранения файлов),
        # тоже можно было бы использовать, но я так и не определился с тем
        # какой из подходов лучше, так что я выбрал хранить файлы в бинарном
        # виде в самой БД.
        if pet.photos != '':
            pet.photos += ';'
        pet.photos += f'{photo.uuid}'
        db.session.commit()

        return photo_to_dict(photo, id)


@pet_namespace.route('/<string:id>/photo/<string:id_photo>')
class PetPhotoGetResource(Resource):
    @check_api_key
    def get(self, id, id_photo):
        pet = PetModel.query.get_or_404(id)
        if id_photo not in pet.photos.split(';'):
            abort(404)
            return

        photo = PhotoModel.query.get_or_404(id_photo)

        response = make_response(photo.binary)
        response.headers.set('Content-Type', photo.content_type)
        response.headers.set(
            'Content-Disposition', 'attachment',
            filename=f'{photo.uuid}.{photo.extension}')

        return response


def main():
    flask_app.run(port=9090, debug=True)


if __name__ == '__main__':
    main()
