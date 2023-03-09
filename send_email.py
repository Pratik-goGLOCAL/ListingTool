from send_mail import SendMail
import streamlit as st
import os
import pickle
import pandas as pd


# names = list(keyword_list.values())

def send_email(r_email,filename):
    with open('DataStore/keyword_list.pickle', 'rb') as handle:
        keyword_list = pickle.load(handle)
    tag = list(keyword_list.keys())[0]
    if tag=='ASIN':
        names = pd.read_csv('DataStore/'+filename)['ASIN'].tolist()
    else:
        names = st.session_state['Brand_name']
    email_subject = 'Listing QC Results for '+ tag
    email_body = '''Hello,

            The Listing QC check is sucessfully completed for {}!!!
            The results are attached with this mail.
            
            Thanks'''.format(names)
    # Create SendMail object
    new_mail = SendMail(
        # List (or string if single recipient) of the email addresses of the recipients
        [r_email], 
        # Subject of the email
        email_subject,
        # Body of the email
        email_body, 
        # Email address of the sender
        # Leave this paramter out if using environment variable 'EMAIL_ADDRESS'
        'pratik.g@goglocal.com' 
    )

    # If using HTML file
    # new_mail.add_html_file('/path/to/your/html/file')

    # List (or string if attaching single file) of relative or absolute file path(s) to files
    new_mail.attach_files(['DataStore/'+filename,'DataStore/DataDict.csv'])

    # Print SendMail object to confirm email
    print(new_mail)

    # Send the email
    # Leave this parameter out if using environment variable 'EMAIL_PASSWORD'
    new_mail.send('gtpjxmfpswyqzbqy')
    os.remove('DataStore/'+filename)
    st.write('Results successfully sent to your email address!!!')