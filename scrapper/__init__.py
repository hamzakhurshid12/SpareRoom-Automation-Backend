# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from operator import contains, indexOf
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json
from datetime import datetime
import time

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
    
    resp = s.request("POST", url, headers=headers, data=payload)
    return s

def saveHTML(htmlData):
    file = open("response.html", "w+")
    file.write(htmlData)
    file.close()

def getClicks(session):
    response = session.request("GET", "https://www.spareroom.co.uk/api/search-campaigns/23668/statistics")
    stats = json.loads(response.text)
    if("data" in stats):
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
        return clicks
        
    else:
        return 0


def getRoomsRatio(query):
    urlRental = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=offered&search='+query
    resp = requests.request('GET', urlRental)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalRentals = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    if(totalRentals=='1000+'): totalRentals = totalRentals[:-1]
    #print(totalRentals)


    urlWanted = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=wanted&search='+query
    resp = requests.request('GET', urlWanted)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalWanted = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    #print(f'{totalWanted} properties wanted in {query}, while {totalRentals} properties are available to rent!\nRatio of wanted to rental: {round(int(totalWanted)/int(totalRentals),2)}')
    return round(int(totalWanted)/int(totalRentals),2)


def getCountListings(session):
    urlListings = 'https://www.spareroom.co.uk/flatshare/mylistings.pl'
    resp = session.get(urlListings)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    bsObj = bsObj.find('p', {'class': 'navcurrent'})
    if bsObj is not None:
        totalListings = bsObj.findAll('strong')[-1].get_text()
    else:
        totalListings = 0
    #print(f'The total pobsOsted Ads are: {totalListings}')
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
    
    #print(f'The Live Listings are: {LiveListingIds}')
    return LiveListingIds


def renewListings(session):
    listingIDs = getListingIDs(session)
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
    #print(response.status_code)

def getLocationId(session, location):
    url = 'https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=wanted&search=' + location + '&min_rent=&max_rent=&per=pcm&available_search=N&day_avail=22&mon_avail=07&year_avail=2021&min_term=0&max_term=0&days_of_wk_available=&room_types=&furnished=&share_type=&genderfilter=&couples=&min_age_req=&max_age_req=&smoking=&keyword=' 
    resp = session.get(url,allow_redirects=False)
    locationHeader = resp.headers['location']
    #print(locationHeader[60:(len(locationHeader) - 1)])
    return locationHeader[60:(len(locationHeader) - 1)]

def getCountPeople(session, locationId):
    urlPeopleLookingForRoom = 'https://www.spareroom.co.uk/flatmate/flatmates.pl?search_id=' + locationId
    resp = session.get(urlPeopleLookingForRoom)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    totalPeople = bsObj.find('p', {'class': 'navcurrent'}).findAll('strong')[-1].get_text()
    if(totalPeople[-1]=='+'): totalPeople = totalPeople[:-1]
    #print(f'The total number of people looking for rooms are: {totalPeople}')
    return int(totalPeople)

def getPeopleIDs(session,query):
    PeopleIDs = []
    ContactedPeopleIDs = []
    UncontactedPeopleIDs = []
    contactedRest = 0
    locationId=getLocationId(session,query)

    countPeople = getCountPeople(session, locationId)
    for i in range(0,countPeople,10):
        urlPeopleLookingForRoom = 'https://www.spareroom.co.uk/flatmate/flatmates.pl?offset=' + str(i) + '&search_id=' + locationId + '&sort_by=age&mode=list'
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
    #print(f'The total contacted people are: {len(ContactedPeopleIDs)}')
    #print(f'The total uncontacted people are: {len(UncontactedPeopleIDs)}')
    #print(len(ContactedPeopleIDs) + len(UncontactedPeopleIDs))
    #print(f'Contacted People IDs: {ContactedPeopleIDs}')
    #print(f'Uncontacted People IDs: {UncontactedPeopleIDs}')
    return UncontactedPeopleIDs

def messageCount(session, person_id):
    urlSent = 'https://www.spareroom.co.uk/flatshare/mythreads_beta.pl?folder=sent'
    resp = session.get(urlSent)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    threads = bsObj.find('div',{'class':'mythreads--desktop'}).findAll('div',{'class': 'msg_row--replied'})
    thread_id = None
    for thread in threads:
        thread_personId = thread.find('a',{'class':'thread_item thread_replied thread_out'})['data-thread-id']
        if(person_id in thread_personId):
            thread_id = thread_personId
    if(thread_id is not None):
        urlInbox = 'https://www.spareroom.co.uk/flatshare/mythreads_beta.pl?thread_id='+thread_id
        resp = session.get(urlInbox)
        bsObj = BeautifulSoup(resp.text, 'html.parser')
        count = len(bsObj.find('ul',{'class': 'conversation'}).findAll('li'))
        return (count)
    else:
        return 0

def minimumTerm(personId):
    url = 'https://www.spareroom.co.uk/flatshare/flatmate_detail.pl?flatshare_id='+ personId
    resp = requests.request('GET', url)
    bsObj = BeautifulSoup(resp.text, 'html.parser')
    minTerm = bsObj.find('dl', {'class': 'feature-list'}).findAll('dd', {'class':'feature-list__value'})[1].get_text()
    if(minTerm == 'None'): 
        return 24
    else:
        return int(minTerm[:-6])
    
def correctUser(username, password):
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
    
    resp = s.request("POST", url, headers=headers, data=payload)
    if(resp.url == 'https://www.spareroom.co.uk/flatshare/logon.pl'): return False
    else: return True





def main():
    #username = "rooms@propertypeopleni.com"
    #password = "Atlantic"
    username = 'kamrankhadijadj@gmail.com'
    password = 'Khadija?9'
    
    session = getLoginSession(username, password)
    print(correctUser(username, password))
    #'''
    #print(datetime.strptime('2021-07-31T23:00:00Z'))
    '''d1 = datetime(2000,5,1,13,5,12)
    d2 = datetime.now()
    d3 = d2 - d1
    print(d1)
    print(d2)
    print(d3.total_seconds())'''



if __name__ == "__main__":
    main()