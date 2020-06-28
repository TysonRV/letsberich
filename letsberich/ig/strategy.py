from letsberich.ig.ig_services import get_ig_api
from time import time, sleep
import pandas as pd
import numpy as np
import random


# This method manages strategy and returns strategy status
class StrategyOne(object):

    def __init__(self):
        self.status = 'OFF'
        self.account_statistics ={}
        self.previous_position_meets_criteria = [{'epic': 'CS.D.BITCOIN.TODAY.IP', 'status': 'false'},
                                                 {'epic': 'CS.D.LTCUSD.TODAY.IP', 'status': 'false'},
                                                 {'epic': 'CS.D.BCHXBT.TODAY.IP', 'status': 'true'}]
        self.position_meets_criteria = []
        self.transaction_history = []

    def get_status(self, status_request='CHECK'):
        ig_api = get_ig_api()
    # This starts monitoring and buys when signals are right

        if status_request == 'ON':
        # Firstly, select instrument of complete FTSE, DOW30 and S&P to trade automatically depending on parameters
        # Need to find a way to keep the while loop running in the background so that we can stop it whenever we want
            self.status = status_request
            end_time = time() + 30
            price_feed = []

            while time() < end_time:
                instrument_list = ig_api.get_instrument_list()

                for instrument in instrument_list:
                    price_feed_dict = {}
                    price_feed_dict.update({'epic': instrument['epic']})
                    price_feed_dict.update({'currentPrice': instrument['offer']})    # offer is buy price ['EPIC1': ] data_feed is a time series that contains all relevant data for the instrument_list
                    parse_data = ig_api.get_past_price(instrument, data_points=200)  # time series containing past price data. For now we will get this from the API but it could be more efficient to have this info in our DB?
                    parse_data_closePrice = [parse_data_element.get('closePrice').get('ask') for parse_data_element in parse_data]
                    # import ipdb; ipdb.set_trace()
                    # parse_data is a list and needs to be accessed element by element.
                    price_feed_dict.update({'pastClosePrice': parse_data_closePrice})
                    price_feed.append(price_feed_dict)

                self.position_meets_criteria = self._strategy_200movingaverage(price_feed,
                                                            self.previous_position_meets_criteria)    # position_meets_criteria will be a dict of boolean values with True=open trade or False=Close trade and EPIC

                if self.previous_position_meets_criteria[0]['epic'] != "":  #skip if it iś initial iteration#

                    for position in self.position_meets_criteria:
                        #this for loop execute buy or sell depending on what strat is telling
                        pos_st = position['status']
                        prev_pos_st = next((element['status'] for element in self.previous_position_meets_criteria
                                            if element['epic'] == position['epic']), None)
                        instrument = ig_api.get_instrument_characteristics(position['epic'])

                        if pos_st == 'true' and pos_st != prev_pos_st:
                            data_for_position = {
                                'currency_code': 'GBP',
                                'deal_reference': 'TESTPos' + str(random.randint(1,100)),
                                'direction': 'BUY',
                                'epic': position['epic'],
                                'expiry': 'DFB',
                                'force_open': 'True',
                                'guaranteed_stop': 'False',
                                'order_type': 'MARKET',
                                'size': '0.5',
                                'stop_level': str(next((element['currentPrice'] for element in price_feed if element['epic']
                                                   == position['epic'])) * 0.97)
                                }
                            open_position_details = ig_api.open_position_wrapper(data_for_position)
                            self.transaction_history.append(open_position_details)

                        if pos_st == 'false' and pos_st != prev_pos_st:
                            closed_position_details = ig_api.close_position_wrapper(position['epic'])
                            self.transaction_history.append(closed_position_details)

                self.previous_position_meets_criteria = self.position_meets_criteria
                sleep(10)
            return {'transactions': self.transaction_history, 'status': self.status}

        if status_request == 'OFF':
        # This closes all positions and stops monitoring.
            response_dict = ig_api.close_position_wrapper()
            self.status = response_dict['status']
            return {'transactions': self.transaction_history, 'status': self.status}

        if status_request == 'CHECK':
            response_dict = ig_api.get_account_useful_data()
            return {'transactions': response_dict, 'status': self.status}

    def _strategy_200movingaverage(self, price_feed: list, previous_position_meets_criteria: list):
        # this method contains the strategy. I have split this from main method to facilitate changing or plugging in a different strategy
        #
        # /// HERE: code strategy that will come up with update list of boolean to decide whether to buy or sell.
        # strategy example: Calculate average over past 100 prices and if current price in data_feed goes through
        # downwards, then sell (boolean set to false). If goes through upwards, then buy (blooean set to true).
        # Finally, return dict with boole to buy or sell/
        position_meets_criteria = []

        for instrument in price_feed:
            pos_meet_cri_dict = {}
            pos_meet_cri_dict.update({'epic': instrument['epic']})

            past_data_feed_numpy = np.array(instrument['pastClosePrice'])
            moving_avg_200 = np.sum(past_data_feed_numpy[1:200])/200  #pandas rolling method could do this
            if previous_position_meets_criteria[0]['epic'] != '':
                prev_pos_elem_status = next((element['status'] for element in previous_position_meets_criteria
                                             if element['epic'] == instrument['epic']), None)
                #prev_pos_elem_status = [element.get('epic', instrument['epic']).get('status') for element in previous_position_meets_criteria]
            else:
                prev_pos_elem_status = ''

            if instrument['currentPrice'] >= moving_avg_200 and (prev_pos_elem_status != 'true' or prev_pos_elem_status != '' ):
                pos_meet_cri_dict.update({'status': 'true'})
                position_meets_criteria.append(pos_meet_cri_dict)

            if instrument['currentPrice'] < moving_avg_200 and ( prev_pos_elem_status != 'false' or prev_pos_elem_status != '' ):
                pos_meet_cri_dict.update({'status': 'false'})
                position_meets_criteria.append(pos_meet_cri_dict)

        return position_meets_criteria


def get_strategy() -> StrategyOne:
    return StrategyOne()