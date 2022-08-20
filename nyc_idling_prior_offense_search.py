import pandas as pd
from sodapy import Socrata
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import numpy as np

import re, sys, os

#Function makes an API call to NYC Open Data, applies Regex to find the plate and state contained in "violation_details", and 
#compares the input state/plate combination against the state/plate combinations of potential prior violations to find prior
#violations, outputting the information in a format that can be copied into a DEP idling complaint.

def prior_violation_find(lookup_state: str, lookup_plate: str, violation_date: str) -> str:

    #pull all tickets from 2 years prior to the violation date.
    date_60_days_prior =  (datetime.strptime(violation_date, '%m/%d/%Y') - relativedelta(years=2)).strftime('%Y-%m-%d')

    #paramaters to contruct the request
    data_url ='data.cityofnewyork.us'
    data_set ='9wun-asa8'    
    app_token = os.environ['app_token']
    client = Socrata(data_url, app_token)
    #filters applied include specific dates need + columns
    results = client.get(data_set, select="ticket_number,violation_date,hearing_date,hearing_result,violation_details,respondent_last_name",where=f"violation_date>='{date_60_days_prior}' AND (hearing_result = 'STIPULATED' OR hearing_result='DEFAULTED' OR hearing_result='IN VIOLATION') AND violation_details IS NOT NULL ",order='hearing_date ASC',limit=999999999)
    idling_df = pd.DataFrame.from_records(results)

    #pull license plate as the value between either LICENSE PLATE IDLING
    #normalize the plate to remove dashes and spaces and NUMBER
    #some older entires used "LICENSE PLATE NUMBER" instead of "LICENSE PLATE"

    idling_df = idling_df.dropna(subset='violation_details')
    plate_str = 'LICENSE PLATE(.*)IDLING'

    #convert date columns to MM-DD-YYYY format
    date_cols = ['violation_date', 'hearing_date']
    for column in date_cols:
        idling_df[column] = idling_df[column].apply(lambda x: datetime.strptime(x[:10],'%Y-%m-%d'))
        idling_df[column] = idling_df[column].apply(lambda x: datetime.strftime(x, '%m/%d/%Y'))
        
    #create function w/ try/except functionality to see where the function fails.
    #regex function doesn't naturally return a string (need to call the group),
    #and the function fails if it can't match the regex

    def str_split(str_to_find, str_to_search):
        try:
            return re.search(str_to_find,str_to_search).group(1)
        except:
            return np.nan

    idling_df['plate_str'] = idling_df['violation_details'].apply(lambda x: str_split(plate_str,x))
    idling_df = idling_df.dropna(subset='violation_details')
    idling_df['plate_str'] = idling_df['plate_str'].apply(lambda x: str(x).replace("-",""))
    idling_df['plate_str'] = idling_df['plate_str'].apply(lambda x: x.replace("NUMBER",""))
    idling_df['plate_str'] = idling_df['plate_str'].apply(lambda x: x.replace(" ",""))

    #pull state using a "ST LICENSE" pattern.
    idling_df['state_str'] = idling_df['violation_details'].apply(lambda x: str(x).split("LICENSE")[0][-3:].strip())

    repeat_df = idling_df.loc[ (idling_df['plate_str'] == lookup_plate) & (idling_df['state_str'] == lookup_state)].reset_index(drop=True)

    #create a string output in the format recommended by DEP. Create a header and a list of
    #the violations, concatenate to output at the end.

   #Use HTML tags instead of standard UNIX tag to get the page to render correctly. The HTML
   #template will reapply the HTML tags used here.
  
    if repeat_df.empty:
         return "There are no prior violations associated with this plate."
    else:
        total_violations = len(repeat_df)
        respondent = repeat_df['respondent_last_name'][0]
        repeat_str_header = f"{respondent} with {lookup_state} license plate {lookup_plate} has {total_violations} prior violation(s) within the past 2 years of this violation occurrence. For respondents with more than 3 prior violations, only the 3 with the oldest hearing date are listed.<br><br>"
        
        violation_number = ['1st', '2nd', '3rd']

        repeat_str_footer = ""

        for count, violation in repeat_df.iterrows():
            temp_str = f"{violation_number[count]} Offense Occurence -{violation['violation_date']}<br>Respondent - {violation['respondent_last_name']}<br>NOV # -   {violation['ticket_number']}<br>Hearing - {violation['hearing_date']}<br>Hearing Result - {violation['hearing_result']}<br><br>"
            repeat_str_footer = repeat_str_footer + temp_str
            if count == 2:
                break

        return repeat_str_header + repeat_str_footer





    

    
    
    
    
    
    