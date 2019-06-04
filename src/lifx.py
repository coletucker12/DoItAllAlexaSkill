import requests


class Lifx(object):

    def __init__(self, token):
        """
        Init Token
        """
        self.ALL_LIGHTS_URL = "https://api.lifx.com/v1/lights/all"
        self.LIGHT_BY_ID_URL = "https://api.lifx.com/v1/lights/id:{}"

        print("Initilizing LIFX Led Light Controlling Program")

        self.headers = {
            "Authorization": "Bearer {}".format(token)
        }

        if token:
            self.get_lights(light_id="320918fdas98793")
        else:
            self.get_lights(light_id=None)

    def get_lights(self, light_id):

        if light_id:
            print("Getting light of id {}".format(light_id))
            print(self.LIGHT_BY_ID_URL.format(light_id))
        else:
            print("Getting list of all lights...")
            print(self.ALL_LIGHTS_URL)

        # response = requests.get("")
