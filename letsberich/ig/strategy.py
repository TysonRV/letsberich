from letsberich.ig.ig_services import get_ig_api
from time import time, sleep

# This method manages strategy and returns strategy status
class StrategyOne(object):

    def __init__(self):
        self.status = 'OFF'
        self.account_statistics ={}

    def get_status(self, status_request):
        ig_api = get_ig_api()
    # This starts monitoring and buys when signals are right

        if status_request=='ON':
        # Firstly, select instrument of complete FTSE, DOW30 and S&P to trade automatically depending on parameters
        # Need to find a way to keep the while loop running in the background so that we can stop it whenever we want
            self.status = status_request
            end_time = time() + 8 * 3600
            previous_position_meets_criteria = {}

            while time() < end_time:
                instrument_list = ig_api.get_instrument() # instrument_list is a dict with all instrument IDs
                data_feed = ig_api.get_live_data(instrument_list)     # data_feed contains all relevant data for the instrument_list
                position_meets_criteria = self.strategy(data_feed)    # position_meets_criteria will be a dict of boolean values with True=open trade or False=Close trade

                for instrument in data_feed:
                    #this for loop execute buy or sell depending on what strat is telling
                    pos_st = position_meets_criteria[instrument['EPIC']]['status']
                    prev_pos_st = previous_position_meets_criteria[instrument['EPIC']]['status']

                    if pos_st == 'true' and pos_st != prev_pos_st:
                        ig_api.open_position_wrapper(data_feed)
                    if pos_st == 'false' and pos_st != prev_pos_st:
                        ig_api.close_position_wrapper(instrument['EPIC'])

                    previous_position_meets_criteria = position_meets_criteria
                    self.account_statistics = previous_position_meets_criteria
                    sleep(10)



        if status_request=='OFF':
        # This closes all positions and stops monitoring.
            response_dict = ig_api.close_position_wrapper()
            self.status = response_dict['status']
            return self.status

        if status_request=='CHECK':
        # Check strategy status
            return self.status

    def strategy(self, data_feed: dict):
        # this method contains the strategy. I have split this from main method to facilitate changing or plugging in a different strategy
        #
        # /// HERE: code strategy that will come up with update list of boolean to decide whether to buy or sell.
        # strategy example: Calculate average over past 100 prices and if current price in data_feed goes through
        # downwards, then sell (boolean set to false). If goes through upwards, then buy (blooean set to true).
        # Finally, return dict with boole to buy or sell///
        position_meets_criteria={}
        return position_meets_criteria

def get_strategy() -> StrategyOne:
    return StrategyOne()