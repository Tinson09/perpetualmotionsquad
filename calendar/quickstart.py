from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools



def main():
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build('calendar', 'v3', http=creds.authorize(Http()))


    GMT_OFF = '+05:30'   
    EVENT = {
	    'summary': 'Carehack Hackathon',
	    'start':   {'dateTime': '2017-11-26T10:00:00%s' % GMT_OFF},
	    'end':     {'dateTime': '2017-11-26T15:00:00%s' % GMT_OFF},
	    'attendees': [
        {'email': 'kttinson.mec@gmail.com'},
        {'email': 'aasiffaizal.mec@gmail.com'},
        {'email': 'pranoypaulpanakkal.mec@gmail.com'},

    ],
    }

    e = service.events().insert(calendarId='primary',
        sendNotifications=True, body=EVENT).execute()

    print('''*** %r event added:
    Start: %s
    End:   %s''' % (e['summary'].encode('utf-8'),
        e['start']['dateTime'], e['end']['dateTime']))


if __name__ == '__main__':
    main()

