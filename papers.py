__author__ = 'tarun'


import json
import datetime

def new_upper_file(in_file, out_file):
    #ofd = open(out_file,"w+")
    with open(out_file,"w+") as ofd:
        with open(in_file, "r+") as ifd:
            icontents = ifd.read()
            ofd.seek(0)
            ofd.write(icontents.upper())

def decide(input_file, watchlist_file, countries_file):

    try:
        new_upper_file(input_file,"temp_input_file.json")
        new_upper_file(watchlist_file,"temp_watchlist_file.json")
        new_upper_file(countries_file,"temp_countries_file.json")
    #except FileNotFoundException, e:
    #    print ("exception")
    except:
        raise(IOError)

    try:
        input_data = open("temp_input_file.json","r")
        watch_data = open("temp_watchlist_file.json","r")
        country_data = open("temp_countries_file.json","r")
    except:
        raise

    try:
        idata = json.load(input_data)
        wdata = json.load(watch_data)
        cdata = json.load(country_data)
    except:
        print("Invalid Json Files")
        return False #quit program


    reqd_info_key_lst = ['BIRTH_DATE', 'ENTRY_REASON', 'FIRST_NAME', 'FROM', 'HOME', 'LAST_NAME', 'PASSPORT']
    Result_list = [] #append results of each person in this list at the end of for loop.
    decision_list = ["Quarantine", "Reject", "Secondary", "Accept"]


    for i in range(len(idata)):
        #status
        #append in the list at the end
        #check case-sensitivity
        idecision = set()
        idecision.add("Accept")

        #CHECK REQUIRED KEYS
        #If the required information for an entry record is incomplete, the traveler must be rejected.
        idecision.add(check_req_keys(idata[i],reqd_info_key_lst))

        #CHECK WATCH LIST
        #If the traveller has a name or passport on the watch list, she or he must be sent to secondary processing
        idecision.add(check_watch_list(idata[i], wdata))

        #CHECK QUARANTINE
        #If the traveler is coming from or via a country that has a medical advisory, he or she must be send to quarantine.
        idecision.add(check_medi_advi(idata[i],"FROM",cdata))
        idecision.add(check_medi_advi(idata[i],"VIA", cdata))

        #RETUNRNING TO KAN
        #If the reason for entry is returning home and the traveller's home country is Kanadia (country code:KAN),
        #the traveller will be accepted.
        idecision.add(check_returning_home(idata[i]))

        #VISITOR VISA REQUIRED
        #If the reason for entry is to visit and the visitor has a passport from a country from which a visitor
        #visa is required, the traveller must have a valid visa. A valid visa is one that is less than two years old.
        idecision.add(check_visa(idata[i],cdata,"VISIT", "VISITOR_VISA_REQUIRED"))

        #TRANSIT VISA REQUIRED
        #If the reason for entry is transit and the visitor has a passport from a country from which a transit
        #visa is required, the traveller must have a valid visa. A valid visa is one that is less than two years old.
        idecision.add(check_visa(idata[i],cdata,"TRANSIT","TRANSIT_VISA_REQUIRED"))

        idecision.remove(None)
        #print(idecision)

        for item in decision_list:
            if item in idecision:
                Result_list.append(item)
                break

    return Result_list

"""
    with open("testrun2.txt","w+") as a:
        for var in range(len(Result_list)):
            if Result_list[var] != "Accept":
                #print(var, Result_list[var])
                a.write(str(var) + " " + str(Result_list[var] + "\n"))
"""
def check_req_keys(data,lst):
    for element in lst:
        if element not in data.keys():
            return "Reject"

def check_watch_list(data,lst):
    for j in lst:
        if j["PASSPORT"] == data["PASSPORT"] or \
                (j["FIRST_NAME"]==data["FIRST_NAME"] and j["LAST_NAME"] == data["LAST_NAME"]):
            return "Secondary"

def check_medi_advi(data, tag, cdata):
    if tag in data.keys():
        country=data[tag]["COUNTRY"]
        if country in cdata.keys() and cdata[country]["MEDICAL_ADVISORY"]:
            return "Quarantine"

def check_returning_home(data):
    if data["ENTRY_REASON"] == "RETURNING" and data["HOME"]["COUNTRY"] == "KAN":
        return "Accept"

def check_visa(data,cdata, entry_reason, tag):
    home_country = data["HOME"]["COUNTRY"]
    if home_country in cdata.keys():
        if (data["ENTRY_REASON"] == entry_reason and "1" == cdata[home_country][tag]):
            if isVisaValid(data):
                return "Accept"
            else:
                return "Reject"

def isVisaValid(data):
    if "VISA" in data.keys():
        d = datetime.datetime.strptime(data["VISA"]["DATE"],"%Y-%m-%d")
        x=d.year + 2
        d=d.replace(year=x)
        if datetime.datetime.today() <= d:
            return True
    return False

def change_files_case_to_upper(*l):
    for file in l:
        with open(file, "r+") as fd:
            contents = fd.read()
            fd.seek(0)
            fd.write(contents.upper())

"""
print(decide("test_returning_citizen.json", "watchlist.json", "countries.json"))
print(decide("test_watchlist.json", "watchlist.json", "countries.json"))
print(decide("test_quarantine.json", "watchlist.json", "countries.json"))
print(decide("example_entries.json", "watchlist.json", "countries.json"))
"""

#decide("example_entries.json", "watchlist.json", "countries.json")

#print(decide("example_reject.json", "watchlist.json", "countries.json"))

#print(decide("test_date.json", "watchlist.json", "countries.json"))
