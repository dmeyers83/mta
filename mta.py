# python standard library
import json
# third party
import requests
import xmltodict
#dataframe
import pandas as pd
#import library to strip html
from bs4 import BeautifulSoup

Subway_Status = {}

def main():

    SOURCE = 'http://www.mta.info/status/serviceStatus.txt'
    response = requests.get(SOURCE)

    xml_string = response.text
    xml_dict = xmltodict.parse(xml_string)
    json_string = json.dumps(xml_dict)

    data = json.loads(json_string)

    subways = data['service']['subway']['line']

    df = pd.DataFrame.from_dict(subways)

    print (df)


    for i, row in df.iterrows():

        #strip out html of text
        subwayName = row['name']
        statusHtml = str(getattr(row, "text"))
        subwayDate = str(getattr(row, "Date"))
        subwayStatus = str(getattr(row, "status"))
        subwayTime = str(getattr(row, "Time"))


        statusNoHmtl = BeautifulSoup(statusHtml)
        updated_status = u' '.join(statusNoHmtl.findAll(text=True))
        df.at[i, 'text'] = updated_status

        #break out subway lines: ACE -> ' A C E', ' A or C or E', 'A', 'B'
        print(subwayName)
        if len(subwayName) > 1:
            subwayLetters = list(subwayName)
            print(subwayLetters)
            for letter in subwayLetters:
                df = df.append({'name': letter.lower(), 'text': updated_status, 'Date': subwayDate, 'Time': subwayTime, 'status': subwayStatus}, ignore_index=True)


    for i, row in df.iterrows():
        subwayName = row['name']
        statusText = str(getattr(row, "text"))
        subwayDate = str(getattr(row, "Date"))
        subwayStatus = str(getattr(row, "status"))
        subwayTime = str(getattr(row, "Time"))

        #add brackets to look for subway name in text
        letterBrackets = '[' +subwayName.upper() + ']'

        #return true if status has the letter
        textStatusHasLetter = letterBrackets in statusText

        #return good if either there are no status issues, or the status text doesn't contain the letter
        if subwayStatus == "GOOD SERVICE" or textStatusHasLetter == False :
            Subway_Status[subwayName] = 'You are good bro!'
        else:
            Subway_Status[subwayName] = statusText
    print(Subway_Status)





if __name__ == '__main__':
    main()
