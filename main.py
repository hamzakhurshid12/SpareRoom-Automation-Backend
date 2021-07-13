# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
import json
import database

def saveHTML(htmlData):
    file = open("response.html", "w+")
    file.write(htmlData)
    file.close()

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

def getStats(session):
    response = session.request("GET", "https://www.spareroom.co.uk/api/search-campaigns/23668/statistics")
    stats = json.loads(response.text)
    return stats


def getListings(session):
    url = "https://www.spareroom.co.uk/api/search-campaigns/23668/listings"
    response = session.request('GET', url)
    listings = json.loads(response.text)
    return listings


def renewListings(session, listingIDs):
    for listingID in listingIDs:
        url = "https://www.spareroom.co.uk/flatshare/advert_renew.pl?advert_id="+listingID
        session.request('GET', url)


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


def main():
    username = "rooms@propertypeopleni.com"
    password = "Atlantic"

    session = getLoginSession(username, password)
    listings = getListings(session)
    stats = getStats(session)
    print(stats['data'])

    #listingsIDs = []
    #for listing in listings['data']:
    #     listingsIDs.append(listing['id'])
    #renewListings(session, listingsIDs)
    # getRoomsRatio('Belfast')
    # print("Total Rooms to be occupied:"+str(getRoomsOccupancy(session)))


if __name__ == '__main__':
    main()
