#http://web.mta.info/status/ServiceStatusSubway.xml

# python standard library
import json
# third party
import requests
import xmltodict
#dataframe
import re

Subway_LIST = {"1":"", "2":"", "3":"", "4":"", "5":"", "6":"", "7":"", "a":"", "c":"", "e":"", "f":"", "b":"", "n":"", "r":"",
               "q":"", "m":"", "s":"", "j":"", "z":"", "d":"", "g":"","l":"", "si":""}

def main():

    SOURCE = 'http://web.mta.info/status/ServiceStatusSubway.xml'
    response = requests.get(SOURCE)

    xml_string = response.text
    xml_dict = xmltodict.parse(xml_string)
    json_string = json.dumps(xml_dict)

    data = json.loads(json_string)

    subways = data['Siri']['ServiceDelivery']['SituationExchangeDelivery']['Situations']
    for index in range (len(subways['PtSituationElement'])):

        PtSituationElement = subways['PtSituationElement'][index]['Summary']
        print(PtSituationElement)
        if PtSituationElement.get('#text', False) != False:  # has a summary attribute
            summaryText = PtSituationElement['#text']
            print (summaryText)

            affectedSubways = subways['PtSituationElement'][index]['Affects']['VehicleJourneys']['AffectedVehicleJourney']
            print(affectedSubways)
            #API returns a list if there are more than 1 affected lines
            if isinstance(affectedSubways, (list,)):
                for index2 in range(len(affectedSubways)):
                    print (affectedSubways[index2]['LineRef'])
                    line = affectedSubways[index2]['LineRef'].split()  #split MTA NYCT_3 w/ a space
                    line2 = line[1].split('_') #split NYCT_3 with a _
                    line3 = line2[1] #take the num array element
                    Subway_LIST[line3.lower()] = summaryText
            else:
                print(affectedSubways['LineRef'])
                line = affectedSubways['LineRef'].split()
                line2 = line[1].split('_')
                line3 = line2[1]
                Subway_LIST[line3.lower()] = summaryText

    #fill in blank values
    for key, value in Subway_LIST.items():
        if Subway_LIST[key] == '':
            Subway_LIST[key] = 'You are good bro!'

    print(Subway_LIST)


if __name__ == '__main__':
    main()
