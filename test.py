import requests 

BASE = "http://127.0.0.1:5000/"

print(requests.post(BASE + "add_user",
{
    'username':'mazhar', 
    'password':'sherry',
    "role": 'not admin',
     "site_username": 'su',
     "site_password": 'dddd',
     "renew_Hours":65
    
}))

#requests.get(BASE + "users")
#print(response.json())
