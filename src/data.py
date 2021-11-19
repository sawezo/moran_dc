# standard
import json
import requests
from tqdm.notebook import tqdm

# data science
import pandas as pd


def wrangle_row_response(data):
    """
    packages up the response text into a dataframe row
    """
    # unpacking the column header row and data
    headers = json.loads(data)[0] # ordered resulting variable names
    data = json.loads(data)[1:] 

    # framing
    return pd.DataFrame(data=data, columns=headers)

def run_api(KEY, year, geo_ids, code2variable):
    """
    Args:
        KEY (str): census api key
        year (str): year of census data to pull
        geo_ids (list): list of geoids to pull down data for
        code2variable (dict): census feature code to variable name

    Returns:
        df: pandas dataframe
    """
    rows = [] # call for each geo-region 
    for s_c_t_b in tqdm(geo_ids, desc="Calling for data"): 
        s_c_t_b = list(str(s_c_t_b))
        state = "".join(s_c_t_b[:2])
        county = "".join(s_c_t_b[2:5])
        tract = "".join(s_c_t_b[5:11])
        block = "".join(s_c_t_b[11:])

        feature_codes = ",".join(list(code2variable.keys()))
        base_url = URL = f"https://api.census.gov/data/{year}/acs/acs5?"
        URL = f"{base_url}key={KEY}&get=NAME,{feature_codes}&for=block%20group:{block}"\
              f"&in=state:{state}%20county:{county}&in=tract:{tract}"
        
        response = requests.get(URL)
        rows.append(wrangle_row_response(response.text))
        
  
    # stack data
    df = pd.concat(rows)
    df.rename(code2variable, axis=1, inplace=True)
    return df