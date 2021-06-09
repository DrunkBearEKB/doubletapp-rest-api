# _Doubletapp Pet REST API_

### _Description:_

A REST API developed for keeping records of pets (dogs and cats).
It is also possible to upload the list of pets to json via the command line.

---

### _Usage:_

#### _API (Web API)_
_**`START:`**_
Change folder to `api/` and execute `python app.py` in command line or 
just run python `api/app.py` in the command line.

_**`API_KEY:`**_
When making requests, it checks the validity of the `API_KEY` and then, 
depending on the result of the check, processes the request, or issues 
`401 Unauthorized`.
The `API_KEY` is expected in the header.
Stored in the `api/config.ini` configuration file.

_**`METHODS:`**_

* `POST` Pet
      
      # Python3 code
      requests.post(
          "http://127.0.0.1:9090/pets/", 
          json={
              'name': '<STRING: PET'S NAME>',  # Vasya
              'age': <INT: PET'S AGE>,         # 5
              'type: '<STRING: PET'S TYPE>'    # dog
          }, 
          headers={
              'Accept': 'application/json',
              'X-Api-Key': '<STRING: API_KEY>'
          }
      
      # curl -X POST "http://127.0.0.1:9090/pets/" -H "accept: application/json" -H "X-API-KEY: <STRING: API_KEY>" -H "Content-Type: application/json" -d "{ \"name\": \"<STRING: PET'S NAME>\", \"age\": <INT: PET'S AGE>, \"type\": \"<STRING: PET'S TYPE>\"}"
        
* `POST` Pet's photo
      
      # Python3 code
      requests.post(
          "http://127.0.0.1:9090/pets/<STRING: ID_PET>/photo", 
          files={
              'image': open('<STRING: FILE_NAME>', mode='rb')  # 'temp_dir/simon_cat.jpg
          }, 
          headers={
              'Accept': 'application/json',
              'X-Api-Key': '<STRING: API_KEY>'
          }
      
      # curl -X POST "http://127.0.0.1:9090/pets/<STRING: ID_PET>/photo" -H "accept: application/json" -H "X-API-KEY: <STRING: API_KEY>" -H "Content-Type: multipart/form-data" -F "image=@<STRING: FILE_NAME>;type=<STRING: IMAGE_TYPE>"
        
* `GET` Pets

      # Python3 code
      requests.get(
          "http://127.0.0.1:9090/pets/", 
          params={
              'limit': <INT: LIMIT>,            # 30
              'offset': <INT: OFFSET>,          # 3
              'has_photos': <BOOL: HAS_PHOTOS>  # True
          }, 
          headers={
              'Accept': 'application/json',
              'X-Api-Key': '<STRING: API_KEY>'
          }

      # curl -X GET "http://127.0.0.1:9090/pets/?limit=<INT: LIMIT>&offset=<INT: OFFSET>&has_photos=<BOOL: HAS_PHOTOS>" -H "accept: application/json" -H "X-API-KEY: <STRING: API_KEY>"
  
* `GET` Pet's photo

      # Python3 code
      requests.get(
          "http://127.0.0.1:9090/pets/<STRING: ID_PET>/photo/<STRING: ID_PHOTO>",
          headers={
              'Accept': 'application/json',
              'X-Api-Key': '<STRING: API_KEY>'
          }

      # curl -X GET "http://127.0.0.1:9090/pets/<STRING: ID_PET>/photo/<STRING: ID_PHOTO>" -H "accept: application/json" -H "X-API-KEY: <STRING: API_KEY>"
     
* `DELETE` Pet

      # Python3 code
      requests.delete(
          "http://127.0.0.1:9090/pets/", 
          json={
              'ids': <LIST[STRING]: LIST_IDS>  # ["8e0fbd1b-b6fe-4b06-b99e-11008f561d01", "914cdb53-e411-4d2b-b697-29e229f573df", "6ed9eb4e-63b7-44db-8856-6a03e4fb23ec"]
          }, 
          headers={
              'Accept': 'application/json',
              'X-Api-Key': '<STRING: API_KEY>'
          }

      # curl -X DELETE "http://127.0.0.1:9090/pets/" -H "accept: application/json" -H 'X-Api-Key: <STRING: API_KEY>' -d '{"ids": <LIST[STRING]: LIST_PETS_IDS>}'


_**`TESTS:`**_
Change folder to `api/tests/`, start the api application and execute 
`python tests.py` in command line.

#### _CLI (Command line interface)_
_**`INFO:`**_
Outputs information about pets in `json` to stdout.

_**`API_KEY:`**_
For requests, the API_KEY is sent in the header so that there is no 
`401 Unauthorized` error. It is stored in the cli/config.ini configuration 
file.
Stored in the `api/config.ini` configuration file.

_**`START:`**_
Change folder to `cli/` and execute `python cli.py [-h] [has_photos]` in 
command line.

    Positional arguments:
      has_photos  
    
    Optional arguments:
      -h, --help  show this help message and exit

---

### _Required:_

See the file `requirements.txt`

---

### _Commentaries:_

If you pay attention, you can see that there are some problems with the 
imports in the file api/app.py. They occur due to errors:

    ImportError: cannot import the name 'cached_property' from 'werkzeug'
    ImportError: cannot import the name '_endpoint_from_view_func' from 'flask.helpers'

Therefore, some not so good measures were taken:

    werkzeug.cached_property = werkzeug.utils.cached_property
    import flask.scaffold
    flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

Also, if you have other additional tasks that you need to complete, write to 
me in Telegram (`@ivanenkogrigory`). I will gladly try to make them. Thanks.

### _Author:_ 

**Ivanenko Grigoriy, Ural State Federal University, 2021.**
