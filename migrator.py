import requests
import sys
import csv
import json
import time
import string
import random

# functions
def getservicedetails(techtype):
  servicedetails = {"service_class":"0", "serviceability_status": "Not Connected", "technology_type": "", "activation_lead_time": ""}
  if techtype == "FTTH":
    servicedetails["service_class"] = "703"
    servicedetails["serviceability_status"] = "CONNECTED"
    servicedetails["technology_type"] = "LBNCo Fibre to the Home (FTTH) technology"
    servicedetails["activation_lead_time"] = "5 - 7 business days"
  
  if techtype == "VDSL":
    servicedetails["service_class"] = "713"
    servicedetails["serviceability_status"] = "CONNECTED"
    servicedetails["technology_type"] = "LBNCo Fibre to the Basement (VDSL) technology"
    servicedetails["activation_lead_time"] = "5 - 7 business days"

  if techtype == "HFC":
    servicedetails["service_class"] = "733"
    servicedetails["serviceability_status"] = "CONNECTED"
    servicedetails["technology_type"] = "LBNCo Hybrid Fibre Coaxial (HFC) technology"
    servicedetails["activation_lead_time"] = "5 - 7 business days"

  return servicedetails;

def generatepass(size=12, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
  return "".join(random.choice(chars) for _ in range(size));

# Set API URL
api_header = {"content-type": "application/json"}
api_url = "https://mv-dev.amaysim.net/broadband/orders"

# set static values for payload
bulk_migration = True
battery_backup_wanted = False
battery_backup_legals_shown = True
landline_number = ""
hardware_product_code = ""
payment_token = "4239064407821788"
payment_transaction_id = "6ca51bac-a5e4-4cc9-a2c0-94368cc8f1cd"
payment_masked_number = "448563******1788"
payment_card_expiry = "11 / 22"

# generate batch number
migration_batch_id = time.strftime("%Y%m%d%H%M%S")
response_filename = "BulkMigrationResponse_" + migration_batch_id + ".csv"


with open (response_filename,"w", newline="") as f:

  count = 0
  for row in csv.DictReader(iter(sys.stdin.readline, "")):
 
    current_id = row["provider_reference_number"]

    # migration data
    migration_data = { 
      "migration-batch-id" : migration_batch_id,  
      "radius-username": row["radius_username"],
      "radius-password": row["radius_password"],
      "previous-provider": row["previous_provider"],
      "provider-reference-number": row["provider_reference_number"],
      "last-billing-date": row["last_billing_date"]
    }

    broadband_technology = getservicedetails(row["technology_type"])

    broadband_service_address = {
     "sub-premises": row["sub_premises"],
     "street-number": row["street_number"],
     "street-name": row["street_name"],
     "street-type": row["street_type"],
     "city": row["city"],
     "state": row["state"],
     "postcode": row["postcode"]
    }

    billing_address = broadband_service_address
    delivery_address = broadband_service_address

    password = generatepass()

    dict = {}
    dict["type"] = "orders"
    dict["attributes"] = { 
#      "bulk-migration": bulk_migration,
#      "migration-data": migration_data,
      "first-name": row["first_name"],
      "last-name": row["last_name"],
      "email": row["email"],
      "password": password,
      "date-of-birth": row["date_of_birth"],
      "contact-number": row["contact_number"],
      "service-class": broadband_technology["service_class"],
      "serviceability-status": broadband_technology["serviceability_status"],
      "provider": row["wholesale_supplier"],
      "technology-type": broadband_technology["technology_type"],
      "technology-type-code": row["technology_type"],
      "activation_lead_time": broadband_technology["activation_lead_time"],
#      "battery-backup-wanted": battery_backup_wanted,
#      "battery-backup-legals-shown": battery_backup_legals_shown,
      "landline-number": landline_number,
      "service-product-code": row["service_product_code"],
      "hardware-product-code": hardware_product_code,
      "max-speed": row["max_speed"],
      "payment-token": payment_token,
      "payment-transaction-id": payment_transaction_id,
      "payment-masked-number": payment_masked_number,
      "payment-card-expiry": payment_card_expiry,
      "location-id": row["location_id"],
      "broadband-service-address": broadband_service_address,
      "billing-address": billing_address,
      "delivery-address": delivery_address
    }

    data = {}
    data["data"] = dict

    payload = json.dumps(data)

    print("Attempting API request...")
    print(payload)


    try:
      response = requests.post(api_url, data = payload, headers = api_header )
      response.raise_for_status()

      resp_obj = response.json()      
      amaysim_order_id = resp_obj["data"]["id"]
      status_code = response.status_code
      result = "SUCCESS"
      message = "OK"
    except requests.exceptions.HTTPError as e:
      print("API request FAILED: ")
      print(e)

      amaysim_order_id = ""
      status_code = response.status_code
      result = "FAIL"
      message = e.args[0]
    except requests.exceptions.RequestException as e:
      print("API request FAILED: " + e)

      amaysim_order_id = ""
      status_code = ""
      result = "FAIL"
      message = "Non-HTTP Request Error"
      
    out = row.copy()
    out["migration_batch_id"] = migration_batch_id
    out["amaysim_order_id"] = amaysim_order_id
    out["status_code"] = status_code
    out["result"] = result
    out["message"] = message
    
    writer = csv.writer(f)

    if count == 0:
      writer.writerow( out.keys( )  )
      count += 1

    writer.writerow( out.values() )
