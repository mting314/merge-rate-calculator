import pandas as pd
import ntpath

from constants import list_off, time_name, dispatch_name, prio_name, desc_name, dispo_name, call_name

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def determine_officer_initiated(df, cityname):
    officer_initiated = 0
    useless = {"assist","warrant","chase","foot","pursuit","traffic","ETS","routine","executive","parking","walk-in","fire","mark-out","driving","truant"}
    # useless.extend(list_off[city])
    
    description_col = desc_name[cityname]
    
    if "N/A" not in description_col:
        description = df[description_col]
        for word in useless | set(list_off[cityname]):
            if (all(item not in description.lower() for item in ["fired", "gunfire", "firework"])
                and word in description.lower()):
                    officer_initiated = 1
            
    if "N/A" not in dispatch_name[cityname] and any(item in cityname for item in ["Detroit","Los Angeles","Mesa","Portland","Sandy","Springs"]):
        if time_name[cityname] == dispatch_name[cityname]:
            officer_initiated = 1 

    if "Elgin" in cityname:
        if "F" in prio_name[cityname]:
            officer_initiated = 1 

    if "Harlingen" in cityname:
        officer_initiated = 0
        if df["callsource"].lower() == "officer initiated":
            officer_initiated = 1 
    
    if "Richmond" in cityname:
        if df["isselfinitiated"] == "No": 
            officer_initiated = 0 
        if df["isselfinititated"] == "No": 
            officer_initiated = 0
        if df["isselfinitiated"] == "Yes":
            officer_initiated = 1
        if df["isselfinititated"] == "Yes": 
            officer_initiated = 1 

    if "Norwalk" in cityname:
        officer_initiated = 0
        if "officer-initiated" in dispo_name["cityname"]:
            officer_initiated = 1

    if "Reno" in cityname or "Sparks" in cityname:
        if description.lower() == "t":
            officer_initiated = 1
    
    if "San Mateo" in cityname: 
        officer_initiated = 1 if df["sourceofcall"] == "Officer Initiated" else 0
    
    if "Tacoma" in cityname:
        officer_initiated = 1 if df["on_view"] == 1 else 0

    return officer_initiated

def calculate_merge_rate(df, cityname):

    # read in demographic data
    demo_data = pd.read_stata("demographic_data.dta")["fips_tract_10"]

    # preprocessing
    df["FIPS"] = pd.to_numeric(df["FIPS"], errors='coerce')
    df.columns = [x.lower().replace(" ", "_") for x in df.columns]

    df["officer_initiated"] = df.apply(determine_officer_initiated, cityname=cityname, axis=1)
    
    test_data = df.loc[df["officer_initiated"] == 0]

    merged = test_data.merge(demo_data, how="left", left_on="fips", right_on="fips_tract_10")
    total_overall = len(merged)

    # dfs that hold bad entries
    missing_my_fips = merged.loc[merged["fips"].isnull()]
    actual_merge_error = merged.loc[(~merged["fips"].isnull()) & (merged["fips_tract_10"].isnull())]

    return ((total_overall - len(missing_my_fips) - len(actual_merge_error))/total_overall,
        missing_my_fips,
        actual_merge_error
    )

if __name__ == "__main__":
    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter.filedialog import askopenfilename
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filepath = askopenfilename() # show an "Open" dialog box and return the path to the selected file

    filename = path_leaf(filepath)
    cityname = filename[:filename.find("_Dispatch")]

    df = pd.read_csv(filepath)
    df["FIPS"] = pd.to_numeric(df["FIPS"], errors='coerce')
    print(calculate_merge_rate(df, cityname=cityname)[0])