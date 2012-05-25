__author__ = "Ed Hunsinger <edrabbit@edrabbit.com>"
__version__ = "0.1"

import datetime
import httplib
import imaplib
import time
import urllib
import urllib2

# You can find your Access Token and Project Id under Inputs -> API
STORM_ACCESS_TOKEN = 'Your SplunkStorm Access Token'
STORM_PROJECT_ID = 'Your SplunkStorm Project ID'

CHECK_DELAY = 60  # delay between checks in seconds
EMAIL_ADDRESS = 'youremail@server.com'  # for identifying results in Storm
SERVER = 'imap.server.com'
SERVER_PORT = '993'
USERNAME = 'yourusername'
PASSWORD = 'yourpassword'


class StormLog(object):
    """A simple example class to send logs to a Splunk Storm project."""

    def __init__(self, access_token, project_id, input_url=None):
        self.url = input_url or 'https://api.splunkstorm.com/1/inputs/http'
        self.project_id = project_id
        self.access_token = access_token

        self.pass_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.pass_manager.add_password(None, self.url, access_token, '')
        self.auth_handler = urllib2.HTTPBasicAuthHandler(self.pass_manager)
        self.opener = urllib2.build_opener(self.auth_handler)
        urllib2.install_opener(self.opener)

    def send(self, event_text, sourcetype='syslog', host=None, source=None):
        params = {'project': self.project_id,
                  'sourcetype': sourcetype}
        if host:
            params['host'] = host
        if source:
            params['source'] = source
        url = '%s?%s' % (self.url, urllib.urlencode(params))
        try:
            req = urllib2.Request(url, event_text)
            response = urllib2.urlopen(req)
            return response.read()
        except (IOError, OSError):
            # An error occured during URL opening or reading
            raise


def check_mail(email_address, mail_host, mail_port, username, password):
    m = imaplib.IMAP4_SSL(mail_host, mail_port)
    m.login(username, password)
    typ, inbox_count = m.select("INBOX")
    resp, emails_unread = m.search(None, "UNSEEN")
    resp, emails_read = m.search(None, "SEEN")

    def get_count(msguids):
        return len(msguids[0].split())

    timestamp = datetime.datetime.now()
    event = ("%s mailbox=%s, total_inbox_count=%d, unread=%d, read=%d"
             % (timestamp, email_address, int(inbox_count[0]),
                get_count(emails_unread), get_count(emails_read)))
    print event
    log = StormLog(STORM_ACCESS_TOKEN, STORM_PROJECT_ID)
    try:
        result = log.send(event, sourcetype='generic_single_line',
                          host=mail_host, source=mail_host)
        return result
    except httplib.BadStatusLine:
        # If we fail to send the log, just drop it
        return None

if __name__ == '__main__':
    while True:
        check_mail(EMAIL_ADDRESS, SERVER, SERVER_PORT, USERNAME, PASSWORD)
        time.sleep(CHECK_DELAY)
