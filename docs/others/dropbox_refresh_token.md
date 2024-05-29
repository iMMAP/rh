# Generate Dropbox Refresh Token

## 1 - Get Access Code
Visit the below link
```shell
https://www.dropbox.com/oauth2/authorize?client_id=<APP_KEY>&token_access_type=offline&response_type=code
```

## 2 - Get the Refresh token
In the terminal using curl
```shell
curl https://api.dropbox.com/oauth2/token \
    -d code=<ACCESS_CODE_FROM_THE_ABOVE_STEP> \
    -d grant_type=authorization_code \
    -d client_id=<APP_KEY> \
    -d client_secret=<APP_SECRET>
```

The response would be:
```shell
{
   "access_token": "sl.************************",
   "token_type": "bearer",
   "expires_in": 14400,
   "refresh_token": "************************", <-- your REFRESH_TOKEN
   "scope": <SCOPES>,
   "uid": "************************",
   "account_id": "dbid:************************"
}
```