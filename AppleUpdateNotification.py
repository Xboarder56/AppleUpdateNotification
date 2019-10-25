# Author: xboarder56
# Version: 1.1
# Python Version: 3.7+
# PIP Install: bs4, requests
import requests
import sys
from bs4 import BeautifulSoup
from datetime import date
import smtplib
import re

update_name = []
release_date = []
update_url = []
update_info = {}
update_release = []
new_updates = []
update_count = ""
smtp_server = '192.168.1.1'
smtp_port = 25
exclude_beta = True
products = ['macOS', 'iOS', 'iPadOS', 'watchOS', 'tvOS']
sender = 'notification@example.local'
recipients = ['root@example.local', 'user@example.local']
current_date = date.today().strftime("%B %d, %Y")

# Download Apple Releases Page and create Soup Variable
page = requests.get('https://developer.apple.com/news/releases/')
soup = BeautifulSoup(page.text, 'html.parser')
html_url = soup.find_all('article',class_ = 'article thumbnail')

# Loop over the HTML object and extract out required sections
for j in html_url:
    # Extract Update Name
    if j.find('a',class_ = 'article-title external-link') is not None:
        name = j.h2.text
        update_name.append(name)
    # Extract Update Release Date
    if j.find('p',class_ = 'lighter article-date') is not None:
        date = j.p.text
        release_date.append(date)
    # Extract Update URL
    if j.find('button',class_ = 'icon icon-link social-icon') is not None:
        match_url = re.search('data-href="(https:\/\/\S+)"\sdata-share-type', str(j.button)).group(1)
        update_url.append(match_url)

for a, b, c in zip(update_name, release_date, update_url):
    update_info = {'Update Name': a, 'Release Date': b, 'Update URL': c}
    update_release.append(update_info)

# Pull matching key pairs (Update Name: Release Date) only for current date
for release_date in update_release:
    # Loop over product names (iOS, macOS, iPadOS)
    for product_name in products:
        # Check if product name exists in Update Name
        if product_name in release_date.get('Update Name'):
            # Exclude Beta Check
            if exclude_beta == True:
                # Only append releases without beta in the name
                if 'beta' not in release_date.get('Update Name'):
                    # Only Grab updates releases on the current date
                   if current_date in release_date.get('Release Date'):
                       new_updates.append('<br><b>Update Name:</b> ' + release_date['Update Name'] + '<br><b>Release Date:</b> ' + release_date['Release Date'] + '<br><a href="'  + release_date['Update URL'] + '">' + release_date['Update URL'] + '</a><br><br>')
            # Both Beta's and Prod Relases
            else:
                # Only Grab updates releases on the current date
                if current_date in release_date.get('Release Date'):
                    new_updates.append('<br><b>Update Name:</b> ' + release_date['Update Name'] + '<br><b>Release Date:</b> ' + release_date['Release Date'] + '<br><a href="'  + release_date['Update URL'] + '">' + release_date['Update URL'] + '</a><br><br>')

# Count the total updates found
update_count = len(new_updates)

# Don't email if there is no updates
if update_count != 0:
    # Format Email Message Body
    email_body = """From: Apple Update Notification <{}>
To: {}
MIME-Version: 1.0
Content-type: text/html
Subject: {} Apple Update(s) Released Today

<h3>Latest Update(s):</h3></a>
{}
    """.format(sender, ", ".join(recipients), update_count, "\n".join(new_updates[0:]))
    # Try to send email
    try:
        smtpObj = smtplib.SMTP(smtp_server, smtp_port)
        smtpObj.sendmail(sender, recipients, email_body)
        print("Sent Mail")
    except:
        print("Error: unable to send email")
        sys.exit(1)
else:
    print("No Updates Found, No email sent.")
    sys.exit(0)
