__author__ = "Ed Hunsinger <edrabbit@edrabbit.com>"
__version__ = "0.1"

import datetime
import httplib
import imaplib
import time
import urllib
import urllib2

CHECK_DELAY = 60  # delay between checks in seconds
EMAIL_ADDRESS = 'youremail@server.com'  # for identifying results in Storm
SERVER = 'imap.server.com'
SERVER_PORT = '993'
USERNAME = 'yourusername'
PASSWORD = 'yourpassword'


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

if __name__ == '__main__':
    while True:
        check_mail(EMAIL_ADDRESS, SERVER, SERVER_PORT, USERNAME, PASSWORD)
        time.sleep(CHECK_DELAY)
