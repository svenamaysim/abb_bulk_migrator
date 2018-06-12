import requests
import sys
import csv
import json
import time

# Set API URL
url = 'https://mv-qa.amaysim.net/broadband/orders'

count = 0
for row in csv.DictReader(iter(sys.stdin.readline, '')):
 
  current_id = row['id']

  # TODO 
  dict = {}
  dict['type'] = 'orders'
  dict['attributes'] = { "migration-data": { "migration-batch-id": 1, "radius-username": row['radius_username'] } }
  dict['first-name'] = row['first_name']

  data = {}
  data['data'] = dict

  payload = json.dumps(data)
  print( payload )
  # TODO
  headers = {'content-type': 'application/json'}

  r = requests.post(url, data = payload, headers = headers )
  status_code = r.status_code
  
  out = row.copy()
  out['status_code'] = status_code

  writer = csv.writer(sys.stdout)
  if count == 0:
    writer.writerow( out.keys( )  )
    count += 1

  writer.writerow( out.values() )
