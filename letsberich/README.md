Added: 
-view to navigate market
-view to show popular market
-view to show open positions and various data (open positions are created manually on ig.com)

Work In Progress:
-Open and close deals method in through API on ig_services (/positions/otc)
-add empty method to call Strategy
-code strategy in separate class
-interlink everything

Coming Soon:
-Once we understand how to download all data, it is probably 
good to delete most views and just create a method in ig_services
to collect all necessary data to feed to strategy
- I will create a quick diagram so that we can follow it


Note:
-working orders/otc are order request placed to execute at a future date when conditions are met.
-position/otc you can choose whether that is placed immediately or at a set price.