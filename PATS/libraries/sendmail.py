#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Python implementation of the SendMail utility.  Provides code for both SMTP
# and MAPI mail transmission.
#
# Note: The MAPI sending pops up a dialog asking the user if the utility can
# send mail on their behalf.  This isn't suitable for a build process so SMTP
# is used instead.
#
# Derived from the sample at:
#   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/149461
#

#
# global imports 
#
import sys
import re
import cStringIO
import base64
import email.header
import email.mime.multipart
import email.mime.text
import email.Message
import email.Utils
import mimetypes
import os
import quopri
import smtplib

#
# Import the UTF-8 Charset
#
email.Charset.add_charset ('utf-8', email.Charset.QP, email.Charset.QP, 'utf-8')

#
# global variables
#
SMTP_SERVER = "mail.deltacontrols.com"
FROM_ADDRESS = '"Test" <build@deltacontrols.com>'

#
# SendSMTPMail
#   Send e-mail directly to an SMTP server.
#
def SendSMTPMail(From="", To="", Subject="", Message="", HTMLMessage="", Attachments=[]):
  mainMsg=email.mime.multipart.MIMEMultipart('alternative')
  mainMsg["To"]=To
  mainMsg["From"]=From
  mainMsg["Subject"]="%s"%email.header.Header(Subject,'utf-8') #Subject
  mainMsg["Date"]=email.Utils.formatdate(localtime=1)
  mainMsg["Message-ID"]=email.Utils.make_msgid()
  mainMsg["Mime-version"]=u"1.0"
  mainMsg["Content-type"]=u"Multipart/mixed"
  mainMsg.preamble=u"Mime message\n"
  mainMsg.epilogue=u"" # To ensure that message ends with newline
  
  if ((Message <> None) and (len(Message) > 0)):
    TextSubMsg = email.mime.text.MIMEText(text.encode('utf-8'), 'plain', 'UTF-8')
    mainMsg.attach(TextSubMsg)
  
  if ((HTMLMessage <> None) and (len(HTMLMessage) > 0)):
    HTMLSubMsg = email.mime.text.MIMEText(HTMLMessage.encode('utf-8'), 'html', 'UTF-8')
    mainMsg.attach(HTMLSubMsg)
  
  # Encode and attach the file attachments
  if ((Attachments <> None) and (len(Attachments) > 0)):
    for FileName in re.split('\;',Attachments):
      contentType,ignored=mimetypes.guess_type(FileName)
      if contentType==None: # If no guess, use generic opaque type
        contentType="application/octet-stream"
      contentsEncoded=cStringIO.StringIO()
      f=open(FileName,"rb")
      mainType=contentType[:contentType.find("/")]
      if mainType=="text":
        cte="quoted-printable"
        quopri.encode(f,contentsEncoded,1) # 1 for encode tabs
      else:
        cte="base64"
        base64.encode(f,contentsEncoded)
      f.close()
      subMsg=email.Message.Message()
      subMsg.add_header("Content-type",contentType,name=FileName)
      subMsg.add_header("Content-transfer-encoding",cte)
      subMsg.set_payload(contentsEncoded.getvalue())
      contentsEncoded.close()
      mainMsg.attach(subMsg)

  # Mail the Message
  smtp = smtplib.SMTP(SMTP_SERVER)
  smtp.sendmail(From, To, mainMsg.as_string())
  smtp.quit()


#
# Usage
#
def Usage():
  print "Python.exe", sys.argv[0], "-u -p -r [-c][-s][-m][-f][-v][-?]"
  print "Where..."
  print ""
  print "-u  login name (user mailbox) of sender)"
  print "-p  login password"
  print "-r  recipient(s) (multiple names must be separated by ';' and"
  print "    must not be ambiguous in default address book.)"
  print "-c  specifies mail copy list (cc: list)"
  print "-s  subject line"
  print "-m  specifies contents of the mail message"
  print "-f  path and file name(s) to attach to message"
  print "-v  generates verbose output"
  print "-?  prints this message"

#
# Main
#
def Main():
  MAPIProfile = None
  SendTo = None
  SendCC = None
  SendBCC = None
  SendSubject = None
  SendMessage = None
  SendAttachments = None
  SendHTMLMessage = None
  Verbose = False
   
  i=1
  while i < len(sys.argv):
    if sys.argv[i] == '':
      i += 1
      continue
    if sys.argv[i] == '-u':
      # user not implemented, use default user
      i += 2
      continue
    if sys.argv[i] == '-p':
      # password not implemented, use default user
      i += 2
      continue
    if sys.argv[i] == '-r':
      i = i+1
      SendTo = sys.argv[i]
      i = i+1
      continue
    if sys.argv[i] == '-c':
      i = i+1
      SendCC = sys.argv[i]
      i = i+1
      continue
    if sys.argv[i] == '-s':
      i = i+1
      SendSubject = sys.argv[i]
      i = i+1
      continue
    if sys.argv[i] == '-m':
      i = i+1
      SendMessage = sys.argv[i]
      i = i+1
      continue
    if sys.argv[i] == '-f':
      i = i+1
      SendAttachments = sys.argv[i]
      i = i+1
      continue
    if sys.argv[i] == '-v':
      Verbose = True
      i += 1
      continue
    if sys.argv[i] == '-?':
      Usage()
      return
    # token not found
    Usage()
    return

  if ((SendTo == None) or
      (SendSubject == None)):
    Usage()
    return

  if (Verbose == True):
    print "To:", SendTo
    print "CC:", SendCC
    print "Subject:", SendSubject
  
  # loop through to address list and send to each person individually, 
  for ToAddress in re.split('\;',SendTo):
    SendSMTPMail(From=FROM_ADDRESS, 
                 To=ToAddress, 
                 Subject=SendSubject, 
                 Message=SendMessage, 
                 HTMLMessage=SendHTMLMessage, 
                 Attachments=SendAttachments)


if __name__ == "__main__":
  Main()
