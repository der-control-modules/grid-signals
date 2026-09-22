# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2022, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}


import logging
import pandas as pd
import sys
import os
import gevent
from datetime import datetime, timedelta
from volttron.platform.agent import utils
from volttron.platform.agent.utils import format_timestamp, get_aware_utc_now
from volttron.platform.messaging import topics
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.scheduling import cron
from volttron.platform.jsonrpc import RemoteError
from dateutil import parser
import dateutil
from price_signal import tou, comed, pjm
from co2_signal import co2_api

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '1.0'


class GridSignalAgent(Agent):
    def __init__(self, config_path, **kwargs):
        super(GridSignalAgent, self).__init__(**kwargs)
        file_config = utils.load_config(config_path)
        default_config = { 
                "campus": "PNNL",
                "run_dayahead_schedule": "0 0 * * *",
                "run_realtime_schedule": "0 * * * *",
                "type_of_grid_service_signals": {
                    "price": {
                        "type_of_price_signal": "TOU",
                        "type_of_tou_pricing": "standard",
                        "TOU_pricing": {
                            "interval":{"off-peak":[[0, 7], [21, 23]], "mid-peak":[[7, 10], [18, 21]] , "on-peak":[[10, 18]]},
                            "pricing":{"off-peak": 0.13246, "mid-peak": 0.15878, "on-peak": 0.19598}
                            }
                        },
                    "co2": {
                            "real-time":true,
                            "method":"API",
                            "API_information": {
                            "API_key": "<your_electricity_maps_api_key>",
                            "zone":"US-CAL-BANC"
                            }
                        }
                    }
                }
        if file_config:
            self.default_config = file_config
        else:
            self.default_config = default_config
        try:
            self.localtz = dateutil.tz.tzlocal()
        except:
            _log.warning(
                "Problem automatically determining timezone! - Default to UTC.")
            self.localtz = "UTC"

        # Initialize variables
        self.signal_type = None
        self.price_type = None
        #self.interval = self.config.get("interval", 5)
        self.publish_topic = None
        self.price_signals = None
        self.grid_service_signals = None
        self.co2_config = None
        self.run_dayahead_schedule = "0 * * * *"
        self.run_realtime_schedule = "0 * * * *"

        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.configure_main,
                                  actions=["NEW", "UPDATE"],
                                  pattern="config")
        self.tou_price_profile_generator = None

        # self.pub_lock = False

    def configure_main(self, config_name, action, contents):
        """This triggers configuration of the Grid service agent via
        the VOLTTRON configuration store.
        :param config_name: canonical name is config
        :param action: on instantiation this is "NEW" or
        "UPDATE" if user uploads update config to store
        :param contents: configuration contents
        :return: None
        """
        _log.debug("Update %s for %s", config_name, self.core.identity)
        config = self.default_config.copy()
        config.update(contents)
        campus = config.get("campus", "")
        self.publish_device_topic = "devices/{}/{}".format(
            campus, "grid_information")
        self.publish_record_topic = "record/{}/{}".format(campus, "grid_information")
        
        # Handle actions for new or updated configurations
        if action == "NEW" or action == "UPDATE":
            # Schedule and additional parameters can be set here as needed
            self.run_dayahead_schedule = config.get("run_dayahead_schedule", None)
            self.run_realtime_schedule = config.get("run_realtime_schedule", None)
            
            # Example of how to handle nested configuration for pricing
            self.grid_service_signals = config.get("type_of_grid_service_signals", {})
            self.price_signals = self.grid_service_signals.get("price", {})
            
            if self.price_signals:
                #next_run = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                #self.tou_price_profile_generator = tou.PriceProfileGenerator(self.price_signals)
                next_run = datetime.now() + timedelta(minutes=2)
                self.core.schedule(next_run, self.generate_price_signal)
                self.core.schedule(cron(self.run_dayahead_schedule), self.generate_price_signal)
                
            # Handle CO2 signals if present
            self.co2_config = self.grid_service_signals.get("co2", {})
            print(f"Co2 = {self.co2_config}")
            
            if self.co2_config:
                _log.debug(f"co2 config is not non")
                co2_api_key = self.co2_config.get("API_information", {}).get("API_key", None)
                co2_zone = self.co2_config.get("API_information", {}).get("zone", None)
                self.co2_signal = co2_api.ElectricityMapsAPI(co2_api_key, co2_zone )
                next_run = datetime.now() + timedelta(minutes=2)
                self.core.schedule(next_run, self.generate_next_24_co2_signal)
                self.core.schedule(cron(self.run_dayahead_schedule), self.generate_next_24_co2_signal)
                if self.co2_config.get("real-time"):
                    _log.debug(f"real-time presentation")
                    self.core.schedule(cron(self.run_realtime_schedule), self.generate_real_time_co2)
                
        
    def generate_real_time_co2(self):
        self.co2_real_time_pub(self.co2_signal.get_co2_intensity(), 'carbonIntensity')
        self.co2_real_time_pub(self.co2_signal.get_power_breakdown(), 'powerConsumptionBreakdown')
        
    def co2_real_time_pub(self, data, point_name):
        print(f"data = {data}")
        if data is not None:
            headers = {'Date': format_timestamp(pd.to_datetime(data['datetime']))}
            message = {point_name:data[point_name]}
            topic_name = self.publish_record_topic + f"/co2/real_time/{point_name}"
            self.publish_data(headers, message, topic_name)
    
    def update_load_list(self, _hour, data):
        ld = []
        for ind in range(_hour, 24):
            ld.append(data[ind])
        for ind in range(0, _hour):
            ld.append(data[ind])
        return ld

    def generate_price_signal(self):
        # Generate price signal value
        _log.debug(f"In generate price signal")
        type_of_price_signal = self.price_signals.get("type_of_price_signal", {})
        if type_of_price_signal.upper() == "TOU":
            self.tou_pricing = self.price_signals.get("TOU_pricing")
            tou_price = tou.PriceProfileGenerator(self.tou_pricing).generate_profile()
            _log.debug(f"TOU price signal = {tou_price}")
        
        ind = datetime.now().hour
        tou_price = self.update_load_list(ind, tou_price)
            
        for i in range(len(tou_price)):
            pub_time = (get_aware_utc_now() + timedelta(hours=i+1)).replace(minute=0, second=0, microsecond=0)
            headers = {'Date': format_timestamp(pub_time)}
            message = [{"tou": float(tou_price[i])},
                    {"tou": {"units": "cents", "tz": "PST", "type": "float"}}]
            topic_name= self.publish_device_topic + "/price/all"
            self.publish_data(headers, message, topic_name)
            
    def shift_24hr(self, data, point_name):
        if data is not None:
            print(f"data = {data}")
            for entry in data['history']:
                new_datetime = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00')) + timedelta(hours=24)
                headers = {'Date': format_timestamp(new_datetime)}
                message = {point_name: entry[point_name]}
                topic_name = self.publish_record_topic + f"/co2/forecast/{point_name}"
                self.publish_data(headers, message, topic_name)

    def generate_next_24_co2_signal(self):
        # Generate CO2 signal value
        co2_intensity_24hr = self.co2_signal.get_24hr_co2_intensity()
        power_breakdown_24hr = self.co2_signal.get_24hr_power_breakdown()
        self.shift_24hr(co2_intensity_24hr, 'carbonIntensity')
        self.shift_24hr(power_breakdown_24hr, 'powerConsumptionBreakdown')
        
    
    def publish_data(self, headers, message, topic):
        # publish given message in the volttron's message bus
        try:
            self.vip.pubsub.publish('pubsub', topic,
                                    headers=headers, message=message).get(timeout=25)

        except Exception as err:
            _log.error("In Publish: {}".format(str(err)))


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(GridSignalAgent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
