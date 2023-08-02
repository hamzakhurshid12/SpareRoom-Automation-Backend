# SpareRoom-Automation-Backend



## USER INFO (VIEWED ONLY BY ADMIN):
```
	/all_users ("GET" to get all the users information)
	/add_user  ("POST" input: username, email, password to register a new user)
	button: Directly moves to login page
```

## LOGIN PAGE:

 ```
/user ("GET" input: email)
```

	* After Login:
	```
  /user ("PUT" input: spareroom_username, spareroom_password, renew_hours, role, password
	/user_messages ("POST" input: email, shortTermMessage, midTermMessage, longTermMessage, followUpMessage, followUpDuration)
	/user_area ("POST" input: email, area_name)
 ```
## ACCOUNT DETAILS:
	```
  update spareroom account
	update password
	/user ("PUT" input: spareroom_username, spareroom_password, renew_hours, role, password
	```

 ## ANALYTICS:
	```
 /user_stats_duratioon ("GET" input: email, days)
	/user_area ("GET", input: email)
	for all the areas:
		/area ("GET" input: area_name)
```

## MESSAGES:
```	
 /user_messages ("GET" input: email)
	/user_messages ("PUT" input: email, shortTermMessage, midTermMessage, longTermMessage, followUpMessage, followUpDuration )
	only renew_hours will be updates:
	/user ("PUT" input: spareroom_username, spareroom_password, renew_hours, role, password
```
## LOGS:
```
	/user_logs ("GET" input: email)
```
