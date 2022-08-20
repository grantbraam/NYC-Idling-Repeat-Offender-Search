**Purpose**: To find prior offenses for a given respondent/license plate combination and output the prior offenses in a format recommended by NYC DEP to include in the complaint.

**Usage**: Input license plate state, number and date violation occured. Output can be directly copied into complaint form. Can run Python file directly or use compiled version. Compiled version has slow start up but can run on its own. Using Python interface requires importing the conda environment. Since the script pulls directly from NYC Open Data during every run, no regular maintenance of the program is required, barring any format changes in the data set.

**Technical Details**: Uses regex to locate plate states + numbers in the "Violation Details" section of the idling data set released by NYC Open Data available here: https://data.cityofnewyork.us/City-Government/idling/ywmm-h8es

**Business logic**:  
-Looks for plate # between the words "LICENSE PLATE" and "IDLING".  
-Looks for state name before the word "LICENSE"  
-When searching for prior violations, uses the logic below (as defined by DEP):  
  -violation has occurred in the past 2 years of the current alleged violation date  
  -violation has been ruled "STIPULATED", "DEFAULTED", or "IN VIOLATION"  
-output format is in format recommended by DEP via email  

**Accuracy**:  
-Using Regex to convert plate numbers was successful at converting 99.85% of offenses that occured in the past 2 years as-of 8/15/2022 (date of the test).  
-Similar accuracy was acheived on state conversion.  
-Conversion accuracy is limited by non-standard language used in some earlier tickets (some mispellings of license/plate, non-standard language, etc.)  
-Script can be used without ongoing updates because it pulls directly from the open data source, meaning that the user is getting the most up-to-date every run  

**Speed**:  
-Near instantaneous start if running native Python.  
