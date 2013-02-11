# Config is a list of dictionnaries
# Each dictionnary looks like : 
# { 'request' : '', 'key' : '' , 'value' : ''}
# where
# request : the SQL request to be executed
# key :  part of the graphite metric name : If key is a list, then grab data from requests, otherwise if it is a string just add it to the metric_name
# value : list of columns of the sql request you want to send to graphite
# 
# Format of the metric name : 
#
# metric_prefix + server_name + metrictype + key + value

import logging

config = [
               {'request' : 'SELECT table_schema AS database_name , table_name AS table_name ,table_rows rows, data_length data_length, index_length idx_length, data_length+index_length total_size, round(index_length/data_length,2) idxfrac FROM information_schema.TABLES where table_schema NOT IN ("information_schema","performance_schema") ORDER BY table_schema DESC ;', 
                'key' : ['database_name','table_name'],
                'metrictype' : 'tablesize',
                'metric_prefix' : 'mysql',
                'value' : ['rows','data_length', 'idx_length','total_size', 'idxfrac']
              },
]

carbon_server = '127.0.0.1'
# Only Pickle Mode is supported
carbon_port = '2004'
# Max number of items per packets.
pickle_max_items_per_packet = 500

# Loglevel
loglevel = logging.INFO


