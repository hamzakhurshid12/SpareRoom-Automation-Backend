# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from operator import indexOf
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json

from requests.sessions import session
import database
import datetime

from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


def getCSRFToken(session):
    url = "https://www.spareroom.co.uk/flatshare/logon.pl"
    resp = session.get(url)  # sets cookie
    bsObj = BeautifulSoup(resp.text, "html.parser")
    csrftoken = bsObj.find('div', {'id': 'userAuth'})['data-csrf-token']
    csrftoken = quote(csrftoken)
    return csrftoken

def getLoginSession(username, password):
    url = "https://www.spareroom.co.uk/flatshare/logon.pl"
    username = quote(username)
    password = quote(password)
    s = requests.session()
    payload = f'csrf_token={getCSRFToken(s)}' \
              f'&email={username}&loginfrom_url=%252F&password={password}&remember_me=N&sign-in-button= '

    headers = {
        'Upgrade-Insecure-Requests': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    s.request("POST", url, headers=headers, data=payload)
    return s

def saveHTML(htmlData):
    file = open("response.html", "w+")
    file.write(htmlData)
    file.close()

def getClicks(session):
    response = session.request("GET", "https://www.spareroom.co.uk/api/search-campaigns/23668/statistics")
    stats = json.loads(response.text)
    clicks = int(stats['data'][0]['clicks_search'])
    date = stats['data'][0]['date']
    if(clicks==0):
        for i in range(1,20):
            clickTemp = int(stats['data'][i]['clicks_search'])
            dateTemp = stats['data'][i]['date']
            if(clicks!=0): 
                clicks = clickTemp
                date = dateTemp
                break

    print(f'The clicks on {date} are {clicks}')
    return clicks


def getRoomsRatio(query):
    urlRental = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=offered&search='+query
    resp = requests.request('GET', urlRental)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalRentals = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()

    urlWanted = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=wanted&search='+query
    resp = requests.request('GET', urlWanted)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalWanted = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    print(f'{totalWanted} properties wanted in {query}, while {totalRentals} properties are available to rent!\nRatio of wanted to rental: {round(int(totalWanted)/int(totalRentals),2)}')
    return round(int(totalWanted)/int(totalRentals),2)


def getCountListings(session):
    urlListings = 'https://www.spareroom.co.uk/flatshare/mylistings.pl'
    resp = session.get(urlListings)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalListings = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    print(f'The total posted Ads are: {totalListings}')
    return int(totalListings)

def getListingIDs(session):
    LiveListingIds = []
    totalListing = getCountListings(session)

    for i in range(0, totalListing, 10):
        urlListings = 'https://www.spareroom.co.uk/flatshare/mylistings.pl?offset=' + str(i)
        resp = session.get(urlListings)
        bsObj = BeautifulSoup(resp.text, 'html.parser')
        LiveListings = bsObj.findAll('div',{'class': 'myListing live'})
        BeforeAdString = 'Ad ref # '
        for liveListing in LiveListings:
            AdRef = liveListing.find('span',{'class':'ad_ref'}).get_text()[len(BeforeAdString):]
            LiveListingIds.append(AdRef)
        if(len(LiveListings)<10): break
    
    print(f'The Live Listings are: {LiveListingIds}')
    return LiveListingIds


def renewListings(session, listingIDs):
    for listingID in listingIDs:
        url = "https://www.spareroom.co.uk/flatshare/advert_renew.pl?advert_id="+ listingID
        session.request('GET', url)

def sendMessage(session, userId, message):
    url = f"https://www.spareroom.co.uk/flatshare/flatmate_detail.pl?flatshare_id={userId}&mode=contact&submode=byemail"
    payload = f'flatshare_id={userId}' \
              f'&message={message}&action=sendemail&mode=contact&submode=byemail&flatshare_type=wanted&M_context=105&M_context_for_link=115&search_id=1053077568'

    headers = {
        'upgrade-insecure-requests': '1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    response = session.request("POST", url, headers=headers, data=payload)
    print(response.status_code)

def getLocationId(session, location):
    url = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=wanted&search=' + location + '&min_rent=&max_rent=&per=pcm&available_search=N&day_avail=22&mon_avail=07&year_avail=2021&min_term=0&max_term=0&days_of_wk_available=&room_types=&furnished=&share_type=&genderfilter=&couples=&min_age_req=&max_age_req=&smoking=&keyword=' 
    resp = session.get(url,allow_redirects=False)
    locationHeader = resp.headers['location']
    print(locationHeader[60:(len(locationHeader) - 1)])
    return locationHeader[60:(len(locationHeader) - 1)]

def getCountPeople(session, query):
    urlPeopleLookingForRoom = 'https://www.spareroom.co.uk/flatmate/flatmates.pl?search_id=' + getLocationId(session, query)
    resp = session.get(urlPeopleLookingForRoom)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalPeople = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    if(totalPeople[-1]=='+'): totalPeople = totalPeople[:-1]
    print(f'The total number of people looking for rooms are: {totalPeople}')
    return int(totalPeople)

def getPeopleIDs(session,query):
    PeopleIDs = []
    ContactedPeopleIDs = []
    UncontactedPeopleIDs = []
    contactedRest = 0
    countPeople = getCountPeople(session, query)
    for i in range(0,countPeople,10):
        urlPeopleLookingForRoom = 'https://www.spareroom.co.uk/flatmate/flatmates.pl?offset=' + str(i) + '&search_id=' + getLocationId(session, query) + '&sort_by=age&mode=list'
        resp = session.get(urlPeopleLookingForRoom)
        bsObj = BeautifulSoup(resp.text, 'html.parser')
        PeoplesListings = bsObj.findAll('li',{'class': 'listing-result'})
        for listing in PeoplesListings:
            if(listing.find('span',{'class': 'tooltip savedAd'})):
                contactedRest = 1
                break
            else:
                UncontactedPeopleIDs.append(listing['data-listing-id'])
        if(contactedRest==1):
            break
    print(f'The total contacted people are: {len(ContactedPeopleIDs)}')
    print(f'The total uncontacted people are: {len(UncontactedPeopleIDs)}')
    print(len(ContactedPeopleIDs) + len(UncontactedPeopleIDs))
    print(f'Contacted People IDs: {ContactedPeopleIDs}')
    print(f'Uncontacted People IDs: {UncontactedPeopleIDs}')
    return UncontactedPeopleIDs


class TrafficHour(Resource):
    def get(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        #clicksInLast24Hours = (Hour1:Hour24) get entry againts user_id from table clicks
        #clicksInLast24Hour[0] = clicks['hour 0'] ------- till hour 24
        clicksInLast24Hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
        IndexOfMax = indexOf(max(clicksInLast24Hours))
        CurrentHour = datetime.datetime.now().hour
        PeakHour = CurrentHour - IndexOfMax + 1
        return PeakHour
   
    #call after every hour to update the clicks
    def patch(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        session = getLoginSession(username, password)
        clicksToday = getClicks(session)
        #clicksInLast24Hours = (Hour1:Hour24) get entry againts user_id from table clicks
        #clicksInLast24Hour[0] = clicks['hour 0'] ------- till hour 24
        clicksInLast24Hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
        CLicksFromLast23Hours = sum(clicksInLast24Hours[0:23])
        LastHourClicks = clicksToday - CLicksFromLast23Hours
        #update database such that
        #hour0 = last hour click
        #hour 1 = clicksInLast24Hours[0]
        #hour 24 = clicksInLast24Hours[22]

#-----Register as a resource
api.add_resource(TrafficHour, "/trafficHour/<int:user_id>/")



class RoomsRatio(Resource):
    def get(self, location):
        ratio = getRoomsRatio(location)
        return ratio

#-----Register as a resource
api.add_resource(RoomsRatio, "/roomRatio/<string:location>/")


class RenewListings(Resource):
    def put(self, user_id):
        #read from from
        renew_time = 1
        #set renew time in database using user_id
          
    def patch(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        session = getLoginSession(username, password)
        LiveListingIDs = getListingIDs(session)
        renewListings(session, LiveListingIDs)

#-----Register as a resource
api.add_resource(RenewListings, "/renewListings/<int:user_id>/")

class ContactPeople(Resource):
    def post(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        session = getLoginSession(username, password)
        #read contact message from database against user id 
        contactMessage = 'This is a contact Message'
        #location = form read
        location = 'Belfast'
        PeopleIds = getPeopleIDs(session, location)
        for peopleId in PeopleIds:
            sendMessage(session, peopleId, contactMessage)
            recentlyContactedPeople = " " + peopleId
        recentlyContactedPeople = recentlyContactedPeople[1:]
        #update in the database as recently contacted
    
    def patch(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        session = getLoginSession(username, password)
        #read follow up message from database against user id 
        followUpMessage = 'This is a follow up Message'
        #read from the database
        recentlyContacted = []
        for peopleId in recentlyContacted:
            sendMessage(session, peopleId, followUpMessage)
#-----Register as a resource
api.add_resource(ContactPeople, "/contactPeople/<int:user_id>/")


class ContactMessage(Resource):
    def post(self, user_id):
        #user_name = database query to get username against user id
        #password = database query to get password against user id
        username = 'kamrankhadijadj@gmail.com'
        password = 'Khadija?9'
        session = getLoginSession(username, password)
        #read followUpMessages and contact messages from

        followUpMessage = 'This is an updated follow up Message'
        contactMessage = 'This is an updated contact Message'

        #update these values in a database

#-----Register as a resource
api.add_resource(ContactMessage, "/contactMessage/<int:user_id>/")





















def main():
    username = "rooms@propertypeopleni.com"
    password = "Atlantic"

    #username = "kamrankhadijadj@gmail.com"
    #password = "Khadija?9"
    session = getLoginSession(username, password)
    
    #userId = 15838185
    #message = 'gjkjhkhk'
    #sendMessage(session, userId, message)
    
    #stats = getStats(session)
    #postedAds = getCountListings(session)
    listingIDs = getListingIDs(session)
    #getRoomsRatio('Belfast')
    
    
    renewListings(session, listingIDs)
    #print(len(listingsIDs))
    # print("Total Rooms to be occupied:"+str(getRoomsOccupancy(session)))

    #getCountPeople(session, 'Belsize Park')
    #getPeopleIDs(session, 'Belfast')

    getClicks(session)

if __name__ == '__main__':
    app.run(debug=True)
    


''''
def getRoomsOccupancy(session):
    url = "https://www.spareroom.co.uk/api/search-campaigns/23668/listings"
    response = session.request('GET', url)
    listings = json.loads(response.text)
    totalRooms = 0
    for listing in listings['data']:
        try:
            totalRooms += int(listing['advert']['property']['rooms']['total'])
        except:
            pass
    return totalRooms

def getRenewableListingIDs(session, totalListing):

    #renewableListingIDs = []
    LiveListingIds = []

    for i in range(0, totalListing, 10):
        urlListings = 'https://www.spareroom.co.uk/flatshare/mylistings.pl?offset=' + str(i)
        resp = session.get(urlListings)
        bsObj = BeautifulSoup(resp.text, 'html.parser')

        LiveListings = bsObj.findAll('div',{'class': 'myListing-link myListing-link__activate myListing-link__activate--renew'})
        LiveListingIdsCurrentPage = []
        for liveListing in LiveListings:
            LiveListingIdsCurrentPage.append(liveListing['data-advert-id'])
            LiveListingIds.append(liveListing['data-advert-id'])

        if(len(LiveListingIdsCurrentPage)<10): break
        #for id in LiveListingIdsCurrentPage:
        #    renListing = bsObj.find('div',{'data-advert-id': id})
            #ask Hamza : can't find the button tag cz it changes based on the renew status
        #    renewableListing = renListing.find('button', {'class': 'button button--link'})
        #    if(renewableListing): renewableListingIDs.append(id)
        
        #recheck ask Hamza
        

    print(f'The Live Listings are: {LiveListingIds}')
    #print(f'The renewable Listings are: {renewableListingIDs}')
    
    #return renewableListingIDs


def getListings(session):
    url = "https://www.spareroom.co.uk/api/search-campaigns/23668/listings"
    response = session.request('GET', url)
    listings = json.loads(response.text)
    return listings


# Make Resources within the API

class Session(Resource):
    def get(self, username, password):
        url = "https://www.spareroom.co.uk/flatshare/logon.pl"
        username = quote(username)
        password = quote(password)
        s = requests.session()
        payload = f'csrf_token={getCSRFToken(s)}' \
                f'&email={username}&loginfrom_url=%252F&password={password}&remember_me=N&sign-in-button= '

        headers = {
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        s.request("POST", url, headers=headers, data=payload)
        return s


    
#-----Register as a resource
api.add_resource(Session, "/session/<string:username>/<string:password>")'''