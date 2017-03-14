# WEBMtube
<a href="https://chrome.google.com/webstore/detail/screamer-detector/fifogepncaogafigddbpgmjchmellldl"><img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/chrome/chrome_48x48.png" width="24" /></a>

Service to detect screamers on 2ch.hk

#Requirements
* FFmpeg
* Redis
* SSL certificate

#How to start
1. Start redis server
```
redis-server
```

2. Start app using honcho
```
honcho start
```
