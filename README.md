# youtube-watchlater-organizer
Lets you reorganize videos in your watch later list to various playlists (for watch later hoarders like me!)

In order to use this, you'll have to [create your own API key and Secret from the Google Developer Console](https://developers.google.com/youtube/v3/). Insert them in the correct place inside `secrets.json` and then run app.py.

Note: I've had trouble running this on OS X for some reason; the redirect url seems to have `8080` regardless of what the url is in the redirect list. If others can reproduce, please create an issue for it.
