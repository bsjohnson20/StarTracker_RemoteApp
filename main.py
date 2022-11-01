import logging
from distutils.command.config import config

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import Settings
from kivy.uix.widget import Widget
import requests as r
import json
from kivy.config import ConfigParser

settings_json = '''
[
    {
        "type": "string",
        "title": "IP",
        "desc": "Choose the ip to connect to",
        "section": "General",
        "key": "ip_main"
    },
    {
        "type": "string",
        "title": "Best Pony",
        "desc": "Literally just choose Luna any other and you're exterminated",
        "section": "General",
        "key": "best_pony"
    },
    
    {
        "type": "string",
        "title": "Location",
        "desc": "Location for weather API service",
        "section": "General",
        "key": "loc"
    }
]
'''


# class Segment(Widget):
#   segments = NumericProperty(0)


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.config = LunaApp.returnConfig(self)
        # self.config = App.get_running_app().config
        self.config.read('startracker.ini')
        # self.ids.loc.text =
        #self.ip = NumericProperty(self.config.get('General', 'ip_main'))
        self.ip = self.config.get('General','ip_main')

        logging.basicConfig(filename='logname',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        logger = logging.getLogger('test')

    def runUpdate(self):
        print(self.ids['speed'])

    def weatherAPI(self, location='Redditch'):
        self.config.read('startracker.ini')
        location = self.config.get('General', 'loc')
        with open('WeatherKey.txt','r') as f:
            token = f.readline()

        #token = '0adf8e4333174820955202743221407'
        # self.config.
        x = r.get(f'http://api.weatherapi.com/v1/current.json?key={token}&q={location}')
        logging.info(x.text)
        json_weather = json.loads(x.text)
        weather = json_weather['current']['condition']['text']
        temp = json_weather['current']['temp_c']
        humidity = json_weather['current']['humidity']
        self.ids.weather.text = weather
        self.ids.temp.text = str(temp) + '°C'
        self.ids.humid.text = str(humidity) + '%'

    def transmitStepControl(self, command='command=STEPSTOP', ip='192.168.137.195'): # SEND TRANSMIT CODES TO NODEMCU
        self.ip = self.config.get('General', 'ip_main')
        self.ids.stepper_id.text = command[command.index('=') + 1:-1] # get everything after 'command' - lazy I am
        result = r.get(f'http://{ip}/api?{command}')  # send command to NodeMCU and get the results
        for i in result: # debug
            print(f'Output: {i}')
        print(f'Response code: {result}')
        self.ids.output.text = result.text.strip(',') # didn't work :/
        # print(result) # debugging purposes


class LunaApp(App):
    def __init__(self, **kwargs):
        super(LunaApp, self).__init__(**kwargs)
        self.config = ConfigParser('Luna') # I really don't know how tf this works
        self.config.read('startracker.ini')

    def returnConfig(self):
        return App.get_running_app().config
        # return self.config

    # config.adddefaultsection('General')
    # config.setdefault('General', 'ip_main', '192.168.137.195')
    # print('test')
    def build_config(self, config):

        # Set the default values for the configs sections.
        config.setdefaults('General', {'ip_main': '192.168.137.195',
                                       'best_pony': 'Luna',
                                       'API': '',
                                       'loc': 'unknown'})  # SET DEFAULTS

    def build_settings(self, settings):
        # someone else's code lol
        # Add our custom section to the default configuration object.
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        #     settings.add_json_panel('My Label', self.config, 'settings.json')

        settings.add_json_panel('General', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):

        # Respond to changes in the configuration.

        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(  # I don't think it works
            config, section, key, value))

        if section == "General":
            if key == "loc":
                self.root.ids.loc.text = value  # updates Location whenever it's changed updating UI
            elif key == 'ip_main':
                pass#self.config.read('startracker.ini')

    def close_settings(self, settings=None):
        """
        The settings panel has been closed.
        """
        Logger.info("main.py: App.close_settings: {0}".format(settings))
        super(LunaApp, self).close_settings(settings)  # close buttons

if __name__ == '__main__':
    LunaApp().run()
