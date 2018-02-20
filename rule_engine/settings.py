from pymongo import MongoClient

uri = 'mongodb://localhost:27017/loyalty_engine'
client = MongoClient(uri)
DB = client['loyalty_engine']


LOG_FILE = '/home/yml/Documents/Projects/LoyaltyProgram/loyalty/data_info.log'
