import requests
import uuid
import platform
import hashlib
import os
import globals




api_key = os.getenv("SELLIX_API_KEY")

if not api_key:
    raise RuntimeError("SELLIX_API_KEY environment variable is not set")

def get_hardware_id():
    mac = uuid.getnode()



    plat_id = platform.platform()

    #hash the two id's together

    combined_id = f"{mac} {plat_id}"

    hashed_hardware_id = hashlib.sha256(combined_id.encode()).hexdigest()

    return hashed_hardware_id




def test_shop_api():
    url = "https://dev.sellix.io/v1/self"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

def orders():
    url = "https://dev.sellix.io/v1/orders"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)


def extract_productid_licensekey(product_id):

    version_name, version_id = globals.version

    # Define the path to the license keys folder
    user_path = os.path.expanduser("~")
    botmod_folder = os.path.join(user_path, f"Automated Fishing {version_name}")
    #Create the botmod_folder on user machine
    os.makedirs(botmod_folder, exist_ok=True)


    # Define the path to the bot_type file
    filename = os.path.join(botmod_folder, f"fishing_{version_name}.txt")


    if not os.path.exists(filename):
        product_id = f"{version_id}"
        with open(filename, "w") as file:
            file.write(f"{product_id}\n")





    with open(filename, "r") as file:
        # Read all lines and filter out empty ones after stripping whitespace
        lines = [line.strip() for line in file if line.strip()]

    # Extract the first and last non-empty lines
    product = lines[0]  # First line
    license = lines[-1]  # Last non-empty line

    # Return both the first and last lines
    return product, license




#sets hwid to corrosponding license key
def set_hardware_id(bot_type):

    product, license = extract_productid_licensekey(bot_type)
    print(product, license)
    url = "https://dev.sellix.io/v1/products/licensing/hardware_id"

    payload = {
        "product_id": product,
        "key": license,
        "hardware_id": get_hardware_id()
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, json=payload, headers=headers)

    print(f"Set hwid, for following license : {str(response.text)}")

    #now log the HWID into the corrosponding order






def add_hwid(uniqid):


    url = f"https://dev.sellix.io/v1/orders/{uniqid}/custom_fields"

    payload = {"custom_fields": [
        {
            "name": "hwid",
            "value": f"{get_hardware_id()}"
        }
    ]}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.request("PUT", url, json=payload, headers=headers)

    print(f"Raw Add HWID is {response.text}")

def extract_hwid_uniqid(response_data):
    """
    Extracts the uniqid and hwid from a Sellix API orders response.

    Parameters:
    response_data (dict): The JSON response from the Sellix API containing orders data.

    Returns:
    List of tuples: Each tuple contains the uniqid and hwid (if present), else None for hwid.
    """
    extracted_data = []

    # Loop through all orders in the response
    for order in response_data.get("data", {}).get("orders", []):
        uniqid = order.get("uniqid")
        hwid = None

        # Check if there are custom fields and look for 'hwid'
        for custom_field in order.get("custom_fields", []):
            if custom_field.get("name") == "hwid":
                hwid = custom_field.get("value")
                break

        # Append the uniqid and hwid (could be None if not found)
        extracted_data.append((uniqid, hwid))

    return extracted_data











#check_existing_hwid()

def extract_license_uniqid(bot_type):

    product, license = extract_productid_licensekey(bot_type)


    url = "https://dev.sellix.io/v1/products/licensing/check"

    payload = {
        "product_id": product,
        "key": license,
        "hardware_id": get_hardware_id()
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.request("POST", url, json=payload, headers=headers)
    response_text = response.text
    print(f"HTML request made on url : {url} to extract uniqid")
    """
    Extracts the uniqid from a Sellix API license response.

    Parameters:
    response_data (str): The JSON response from the Sellix API containing license data.

    Returns:
    str: The uniqid from the license data.
    """
    # Parse the JSON string
    data = response.json()
    print(f"Raw data response {data}")

    # Extract the uniqid from the license data
    uniqid = data['data']['license']['uniqid']



    return str(uniqid)







def check_license(bot_type):

    product, license = extract_productid_licensekey(bot_type)

    url = "https://dev.sellix.io/v1/products/licensing/check"

    payload = {
        "product_id": product,
        "key": license,
        "hardware_id": get_hardware_id()
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Make the request
    response = requests.post(url, json=payload, headers=headers)

    # Try to parse the response as JSON
    try:
        response_log = response.json()
        print(f"Checking license... Raw response: {response_log}")
    except ValueError:
        # If response is not valid JSON, print an error and return False
        print("Invalid response format. Could not parse JSON.")
        return False

    # Handle error based on status code or other error key
    if response_log.get("status") != 200:
        print(f"Error finding license: {response_log.get('error', 'Unknown error')}")
        return False

    # If successful, return True
    return True




#contains functions for getting hwid and checking the hwid against orders from order list
def check_existing_hwid(bot_type):
    #extracts current user uniqid and passes as the

    uniqid = extract_license_uniqid(bot_type)
    print(f"UNIQID : {uniqid}")
    add_hwid(uniqid)








    #add logic to check orders list for a matching hwid
    url = "https://dev.sellix.io/v1/orders"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.request("GET", url, headers=headers)

    print(response.text)

    hwid_uniqid = response.json()

    print(hwid_uniqid)












#Takes the bot type being used and completes a license check. Returns True if successful
def start_hwid_license_check(bot_type):
    set_hardware_id(bot_type)
    # Attempt to check the license
    if not check_license(bot_type):
        # Handle the case where the license check fails
        print("Exiting hwid license check, User must re enter a valid License Key")
        #exits back to main loop
        return False
    else:
        print("Future updates after license check system will check all free trial keys for existing hwid")
        return True

    #how do we stop user from making multiple free trial license keys

    #check_existing_hwid

    #call shucker.start_shucker() from main project
bot = "oyster_shucker"








#user boots up first we check their hwid isnt being used already
#check_existing_hwid()








