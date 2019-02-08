import sys
import os

import easyimap
import secrets

attachmentsDir = 'attachments'

def saveDocxAttachment(filename, fileObj):
    if '.docx' in filename:
        if not os.path.exists(attachmentsDir):
            os.makedirs(attachmentsDir)
        f = open(attachmentsDir + '/' + filename, "wb")
        f.write(fileObj)
        f.close()

def main():
    imapAccount = easyimap.connect('imap.gmail.com', secrets.getMailLogin(), secrets.getMailPassword(), mailbox='INBOX', timeout=15, ssl=True,port=993)
    unseenMail = imapAccount.unseen()
    for mail in unseenMail:
        if any(x in mail.from_addr for x in secrets.getTrustedDomains()):
            for attachment in mail.attachments:
                filename = attachment[0]
                fileObj = attachment[1]
                saveDocxAttachment(filename, fileObj)
                
    
    imapAccount.quit()

if __name__ == "__main__":
    sys.exit(main())