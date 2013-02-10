mysql2graphite
==============

mysql2Graphite is a little tool that can execute a custom sql request
to a mysql server and send the result to a graphite server.

This way, you can easily see :

 * the trending of the number of lines in a table
 * the trending of the data size for a specific table or a database
 * the trending of a specific counter

The example given in the config file send for every table for all databases :
 * the number of lines of that table
 * the size of the data
 * the size of the index
 * the sum of the data + index
 * the ratio of index/data

You can also use this script to send mysql performance counters to Graphite.
