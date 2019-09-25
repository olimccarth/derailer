from flask import Flask, request, redirect, session
from twilio.twiml.messaging_response import MessagingResponse
import requests, json
import sqlite3
import re
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

 greeting = session.get('greeting')
 codequestion = session.get('codequestion')
 codecheck = session.get('codecheck')
 code = session.get('code')
 confirmation = session.get('confirmation')
 termsandconditions = session.get('termsandconditions')
 termsandconditionslink = session.get('termsandconditionslink')
 
 codematch = 'TRYDRLR'
 termsandconditionslink = 'https://www.derailer.com/terms-and-conditions'
 promotionalprice = '4.95'
 regularprice = '9.95'
 warehouseaddress = 'c/o Derailer Innovative Deliveries\n1475 Mission Street\nSan Francisco, CA 94103'
 
 number = request.form['From']
 number = number[1:]
 session['number'] = number
 
 resp = MessagingResponse()

 conn = sqlite3.connect('../SQLite/Derailer.sqlite3')
 c = conn.cursor()

 c.execute("INSERT OR IGNORE INTO customers (Phone_number) VALUES ({})".format(number))

 conn.commit()

 if greeting == None:

  resp.message('Hi, thank you for contacting Derailer.')

  greeting = 'Yes'

  test = request.form['Body']

  coderaw = re.search(codematch, test)

  if coderaw == None:

   resp.message('Have you been provided with a promotional code?\n1 - Yes 2 - No')

   codecheck = 'Yes'

   session['codecheck'] = codecheck

   session['greeting'] = greeting

  else:
   
   code = coderaw.group(0)

   resp.message('Thank you for providing your code.')

   session['code'] = code

   session['greeting'] = greeting

   c.execute('SELECT Terms FROM customers WHERE Phone_number={}'.format(number))

   terms = str(c.fetchone)

   for row in c:
    terms = row[0]  
    termsandconditions = terms

   print(terms)

   if termsandconditions == None or termsandconditions == 'sent':

    resp.message('Please click on the following link and respond \'YES\' if you agree to the terms and conditions:\
    https://www.derailer.com/terms-and-conditions\nYou must agree to proceed.')

    termsandconditions = 'sent'
    
    c.execute("UPDATE customers SET Terms=(?) WHERE Phone_number=(?)", (termsandconditions, number))

    conn.commit()

    session['termsandconditions'] = termsandconditions

   else:

    resp.message('To have your item delivered to us, please add the following address after your name when checking out online:\n{}'.format(warehouseaddress))
    resp.message('Once we receive your package we will send you a text at this number to confirm when and where we should deliver the package.\n\
    The price for your delivery will be ${}.'.format(promotionalprice))
    resp.message('Thank you for using Derailer.')

   
 elif codecheck != None and codequestion == None:

  codequestion = request.form['Body']

  if codequestion == '1':

   resp.message('Thank you. Please enter it now.')

   session['codequestion'] = codequestion

  elif codequestion == '2':

    terms = c.execute('SELECT (Terms) FROM customers WHERE Phone_number={}'.format(number))

    terms = str(c.fetchone)

    for row in c:
     terms = row[0]  
     termsandconditions = terms

    print(terms)

    if termsandconditions == None or termsandconditions == 'sent':

     resp.message('Please click on the following link and respond \'YES\' if you agree to the terms and conditions:\
     https://www.derailer.com/terms-and-conditions\nYou must agree to proceed.')

     termsandconditions = 'sent'
    
     c.execute("UPDATE customers SET Terms=(?) WHERE Phone_number=(?)", (termsandconditions, number))

     conn.commit()

     session['termsandconditions'] = termsandconditions

     session['codequestion'] = codequestion

     session['code'] = 'nocode'

    else:

     resp.message('To have your item delivered to us, please add the following address after your name when checking out online:\n{}'.format(warehouseaddress))
     resp.message('Once we receive your package we will send you a text at this number to confirm when and where we should deliver the package.\n\
     The price for your delivery will be ${}.'.format(regularprice))
     resp.message('Thank you for using Derailer.')

     session['codequestion'] = codequestion

     session['code'] = 'nocode'

  else:

   resp.message('Please enter either 1 for Yes or 2 for No.')

 elif code == None: 

  test = request.form['Body']

  coderaw = re.search(codematch, test)

  if coderaw == None and test != '1':

   resp.message('This code does not match our records. Please enter a valid code or text \'1\' to proceed without a code.')

  elif test == '1':

   code = 'nocode'

   session['code'] = code

   c.execute('SELECT (Terms) FROM customers WHERE Phone_number={}'.format(number))

   terms = c.fetchall

   if termsandconditions == None:

    resp.message('Please click on the following link and respond \'YES\' if you agree to the terms and conditions:\
    https://www.derailer.com/terms-and-conditions\nYou must agree to proceed.')

    termsandconditions = 'sent'
    
    c.execute("UPDATE customers SET Terms=(?) WHERE Phone_number=(?)", (termsandconditions, number))

    conn.commit()

    session['termsandconditions'] = termsandconditions

   else:

    resp.message('To have your item delivered to us, please add the following address after your name when checking out online:\n{}'.format(warehouseaddress))
    resp.message('Once we receive your package we will send you a text at this number to confirm when and where we should deliver the package.\n\
    The price for your delivery will be ${}.'.format(promotionalprice))
    resp.message('Thank you for using Derailer.')

  else:

   code = coderaw.group(0)

   resp.message('Thank you for providing your code.')

   session['code'] = code

   if termsandconditions == None or termsandconditions == 'sent':

    resp.message('Please click on the following link and respond \'YES\' if you agree to the terms and conditions:\
    https://www.derailer.com/terms-and-conditions\nYou must agree to proceed.')

   else:

    resp.message('To have your item delivered to us, please add the following address after your name when checking out online:\n{}'.format(warehouseaddress))
    resp.message('Once we receive your package we will send you a text at this number to confirm when and where we should deliver the package.\n\
    The price for your delivery will be ${}.'.format(promotionalprice))
    resp.message('Thank you for using Derailer.')

 elif confirmation == None:

  confirmation = request.form['Body']

  if confirmation == 'Yes' or confirmation == 'YES' or confirmation == 'Y' or confirmation == 'y':

   termsandconditions = 'Agree'
   resp.message('Thank you. To have your item delivered to us, please add the following after your name at checkout:\n{}'.format(warehouseaddress))
   resp.message('Once we receive your package we will send you a text at this number to confirm when and where we should deliver the package.')

   c.execute("UPDATE customers SET Terms=(?) WHERE Phone_number=(?)", (termsandconditions, number))

   conn.commit()

   session['termsandconditions'] = termsandconditions

   if code == 'nocode':
                
    resp.message('The price for your delivery will be ${}.'.format(regularprice))
    resp.message('Thank you for using Derailer.')

   else:
       
    resp.message('The price for your delivery will be ${}.'.format(promotionalprice))
    resp.message('Thank you for using Derailer.')

   session['termsandconditions'] = termsandconditions

  else:

   resp.message('You must agree to the Terms and Conditions to use this service. Please respond \'YES\' if you agree to the terms and conditions.\n')
   
 number = request.form['From']
 message_body = request.form['Body']

 number = number[1:]
 
 print(number, message_body)

 conn.close()

 return str(resp)

if __name__ == "__main__":
 app.run(debug=True)
