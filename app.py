import httplib2
import os
import sys
import SocketServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from multiprocessing import Process

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

PORT = 8082
SERVER_PROC = 0

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_ALTER_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def waitforwebrequest():
    httpd = SocketServer.TCPServer( ('', PORT), SimpleHTTPRequestHandler )
    httpd.serve_forever()

def testlocalserver():
    h = httplib2.Http(".cache")
    notupyet = True
    tries = 0
    resp_headers = None
    while notupyet and tries < 50:
        try:
            (resp_headers, content) = h.request("http://127.0.0.1:%d/oauth.html" % PORT, 'GET')
            notupyet = False
        except:
            tries += 1

    return resp_headers and resp_headers.status == 200

def forkserver():
    global SERVER_PROC 
    SERVER_PROC = Process(target=waitforwebrequest)
    SERVER_PROC.start()

def killserver():
    SERVER_PROC and SERVER_PROC.terminate()

def authorize():

    credentials = None
    # setup a local http server for the authorization
    forkserver()
    if (testlocalserver()):

        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                message=MISSING_CLIENT_SECRETS_MESSAGE,
                scope=YOUTUBE_READONLY_SCOPE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flags = argparser.parse_args()
            credentials = run_flow(flow, storage, flags)

        # tear down local http server
        killserver()

    return credentials

def printWatchLater(yt):

    # Retrieve the contentDetails part of the channel resource for the
    # authenticated user's channel.
    channels_response = yt.channels().list(
      mine=True,
      part="contentDetails"
    ).execute()

    for channel in channels_response["items"]:
      # From the API response, extract the playlist ID that identifies the list
      # of videos uploaded to the authenticated user's channel.
      uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["watchLater"]

      print "Videos in list %s" % uploads_list_id

      # Retrieve the list of videos uploaded to the authenticated user's channel.
      playlistitems_list_request = yt.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=50
      )

      while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Print information about each video.
        for playlist_item in playlistitems_list_response["items"]:
          title = playlist_item["snippet"]["title"]
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]
          print "%s (%s)" % (title, video_id)

        playlistitems_list_request = yt.playlistItems().list_next(
          playlistitems_list_request, playlistitems_list_response)

      print

def listPlaylists(yt):
    pass
#    playlist_response = yt.playlists().list(part="snippet").execute()
#    for playlist in playlist_response["items"]
#        pass
#    for playlist_item in playlist_response["items"]:
#        title = playlist_item["snippet"]["title"]
#            video_id = playlist_item["snippet"]["resourceId"]["videoId"]
#            print "%s (%s)" % (title, video_id)

if __name__ == '__main__':

    # MAIN SCRIPT 

    cred = authorize()

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=cred.authorize(httplib2.Http()))

    #listPlaylists(youtube)
    printWatchLater(youtube)

