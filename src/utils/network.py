import requests

def run_json_query(url:str, json_query:str):
    response = requests.post(url, json={'query': json_query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, json_query))