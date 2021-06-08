import unittest
import configparser
import requests
import uuid

FILE_CONFIG = '../config.ini'


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        config = configparser.ConfigParser()
        config.read(FILE_CONFIG)

        self.__address = 'http://127.0.0.1:9090/'
        self.__headers = {
            'Accept': 'application/json',
            'X-Api-Key': config['Settings']['api_key']
        }

        self.__data = {
            'name': 'vasya',
            'age': 5,
            'type': 'cat'
        }
        self.__data_2 = {
            'name': 'tolya',
            'age': 3,
            'type': 'dog'
        }

    def __post_data(self, data=None, files=None, suffix=''):
        if data is None:
            return requests.post(
                f'{self.__address}pets/{suffix}',
                files=files,
                headers=self.__headers
            )
        if files is None:
            return requests.post(
                f'{self.__address}pets/{suffix}',
                json=data,
                headers=self.__headers
            )
        return requests.post(
            f'{self.__address}pets/{suffix}',
            json=data,
            file=files,
            headers=self.__headers
        )

    def __get_data(self, params):
        return requests.get(
            f'{self.__address}pets/',
            params=params,
            headers=self.__headers
        )

    def __delete_data(self, data):
        return requests.delete(
            f'{self.__address}pets/',
            json=data,
            headers=self.__headers
        )

    def test_pet_post_correct(self):
        response = self.__post_data(
            data=self.__data
        )

        self.assertEqual(200, response.status_code)

        response_json = response.json()
        for key, value in self.__data.items():
            self.assertIn(key, response_json.keys())
            self.assertEqual(value, response_json[key])

    def test_pet_post_incorrect(self):
        response = self.__post_data(
            data=dict(list(self.__data.items())[:2])
        )

        self.assertEqual(400, response.status_code)

    def test_pet_get_correct(self):
        response_post = self.__post_data(
            data=self.__data)
        response_post_json = response_post.json()

        response_get = self.__get_data(
            params={
                'limit': 999999,
                'has_photos': None
            }
        )
        response_get_json = response_get.json()

        self.assertIn(response_post_json['id'],
                      list(map(lambda x: x['id'], response_get_json['items'])))

    def test_pet_get_incorrect(self):
        response_get = self.__get_data(
            params={
                'limit': 'dfd',
                'kaka': 123,
                'has_photos': None
            }
        )

        self.assertEqual(400, response_get.status_code)

    def test_pet_delete_correct(self):
        responses_post_id = []
        for data in [self.__data, self.__data_2]:
            responses_post_id.append(self.__post_data(
                data=data
            ).json()['id'])

        amount_incorrect = 5
        response_delete = self.__delete_data(
            data={
                'ids': responses_post_id +
                       [str(uuid.uuid4()) for _ in range(amount_incorrect)]
            }
        )

        self.assertEqual(200, response_delete.status_code)
        self.assertEqual(len(responses_post_id),
                         response_delete.json()['deleted'])
        self.assertEqual(amount_incorrect,
                         len(response_delete.json()['errors']))

    def test_pet_delete_incorrect(self):
        response_delete = self.__delete_data(
            data={
                'idssss': ['1']
            }
        )

        self.assertEqual(400, response_delete.status_code)

    def test_pet_photo_post_correct(self):
        response_post = self.__post_data(
            data=self.__data
        )
        response_post_json = response_post.json()

        path_to_image = __file__[:__file__.rindex("\\")] + \
                        '/photos/simon_cat.jpg'
        response_post_photo = self.__post_data(
            files={
                'image': open(path_to_image, mode='rb')
            },
            suffix=f'{response_post_json["id"]}/photo'
        )

        self.assertEqual(200, response_post_photo.status_code)

    def test_pet_photo_post_incorrect(self):
        response_post = self.__post_data(
            data=self.__data
        )
        response_post_json = response_post.json()

        path_to_image = __file__[:__file__.rindex("\\")] + \
                        '/photos/simon_cat.jpg'
        response_post_photo = self.__post_data(
            files={
                'SOMETHING BUT NOT IMAGE': open(path_to_image, mode='rb')
            },
            suffix=f'{response_post_json["id"]}/photo'
        )

        self.assertEqual(400, response_post_photo.status_code)


if __name__ == '__main__':
    unittest.main()
