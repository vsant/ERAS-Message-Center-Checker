#!/usr/bin/env python
#
# ERAS Message Center Scraper
#
# Vivek Sant
# 2014-09-29
#

import os
import re
import smtplib
import urllib, urllib2, cookielib, json
from settings import *

fn  = os.path.dirname(os.path.realpath(__file__)) + '/db.txt'

def clean(txt):
  txt = txt.replace('<br>', '\n').replace('<br />', '\n').replace('&nbsp;', ' ').replace('<BR>', '\n').replace('<BR />', '\n')
  p = re.compile(r'<.*?>')
  return p.sub('', txt).strip()

def mail(fr, to, msg, serverURL='', un='', pw=''):
  s = smtplib.SMTP(serverURL)
  if un != '' and pw != '':
    s.starttls()
    s.login(un, pw)
  s.sendmail(fr, to, msg)
  s.quit()

def email(data):
  for i in TO:
    mail(FR, i, MSG % { 'fr':FR, 'to':i, 'msg':data}, MAIL_SERVER, MAIL_UN, MAIL_PW)

def main(args):
  # Log in
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  login_data = urllib.urlencode({ 'username' : un, 'password' : pw })
  opener.open(url_login, login_data)

  # Read inbox
  resp = opener.open(url_inbox).read().strip()

  # Read in db
  cache = []
  if os.path.exists(fn):
    f = open(fn, "r+")
    cache = f.read().strip().split('\n')
    f.close()

  # Iter over msgs - check db
  for m in json.loads(resp):
    ID = str(m['guid']) if m['guid'] != u'' else str(m['msgid'])
    if ID not in cache:
      cache.append(ID)
      url_msg = url_msg_templ % (str(m['guid']), str(m['msgid']))
      msg = json.loads(opener.open(url_msg).read().strip())
      fr = msg["fromAlias"] if "fromAlias" in msg.keys() else msg["frominstitution"]
      email(clean(fr.encode('utf-8')) \
          + "\n" + clean(msg["subject"].encode('utf-8')) \
          + "\n\n" + clean(msg["message"].encode('utf-8')))

  # Write out db file
  f = open(fn, "w")
  for i in cache:
    f.write(i + "\n")

if __name__ == "__main__":
  import sys
  sys.exit(main(sys.argv))
