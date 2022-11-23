from flask import Flask, render_template, request, redirect, url_for, session
from SendGridMail import sendMail
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30875;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jkc20422;PWD=e5hC1j159iI2zSKD",'','')

app = Flask(__name__)
app.secret_key = 'SESSIONKEY'


@app.route("/",methods=['GET'])
def home():
  if 'email' not in session:
    return redirect(url_for('login'))
  return render_template('home.html')

@app.route("/register",methods=['GET','POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phno = request.form['phno']
    bloodGroup = request.form['blood_group']
    address = request.form['address'] or ''
    pincode = request.form['pincode']


    if not email or not username or not password or not phno or not bloodGroup or not pincode:
      return render_template('register.html',error='Please fill all fields')
    
    query = "SELECT * FROM USERS WHERE Email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    
    if not isUser:
      insert_sql = "INSERT INTO Users(NAME,EMAIL,PASSWORD,PHONE,BLOOD_GROUP,ADDRESS,PINCODE) VALUES (?,?,?,?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, username)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, password)
      ibm_db.bind_param(prep_stmt, 4, phno)
      ibm_db.bind_param(prep_stmt, 5, bloodGroup)
      ibm_db.bind_param(prep_stmt, 6, address)
      ibm_db.bind_param(prep_stmt, 7, pincode)
      ibm_db.execute(prep_stmt)
      
      sendMail(email, 'Registered Successfully', 'Hello {}, <br>Thank you for Registering!! 🙂'.format(username))

      return redirect(url_for('login'))
    else:
      return render_template('register.html')

  return render_template('register.html')

@app.route("/login",methods=['GET','POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    loginType = request.form['login-type']

    if not email or not password:
      return render_template('login.html',error='Please fill all fields')
    query = "SELECT * FROM USERS WHERE Email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    print(isUser,password)

    if not isUser:
      return render_template('login.html',error='Invalid Credentials')
      
    #if not isPasswordMatch:
    if(isUser['PASSWORD']!=password):
      return render_template('login.html',error='Invalid Credentials')

    session['email'] = isUser['EMAIL']

    if(loginType == 'donor'):
      return redirect("donor")
    else:
      return redirect("recipient")

  return render_template('login.html')

@app.route("/donor", methods=['GET','POST'])
def addDonor():
  if request.method == 'POST':
    query = "SELECT * FROM USERS WHERE Email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,session['email'])
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    print(isUser)

    insert_sql = "INSERT INTO DONOR(NAME,EMAIL,BLOOD_GROUP,PINCODE) VALUES (?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, isUser['NAME'])
    ibm_db.bind_param(prep_stmt, 2, isUser['EMAIL'])
    ibm_db.bind_param(prep_stmt, 3, isUser['BLOOD_GROUP'])
    ibm_db.bind_param(prep_stmt, 4, isUser['PINCODE'])
    ibm_db.execute(prep_stmt)

    sendMail(session['email'], 'Request for Donation Received', 'Thank you🙏, your request has beed added!')

    return render_template('donor.html', name='Donor Dashboard', request_for_donation=True)
  
  query = "SELECT * FROM DONOR WHERE Email=?"
  stmt = ibm_db.prepare(conn, query)
  ibm_db.bind_param(stmt,1,session['email'])
  ibm_db.execute(stmt)
  isUser = ibm_db.fetch_assoc(stmt)
  print(isUser)
  return render_template('donor.html', name='Donor Dashboard', request_for_donation=isUser)

def getDonorsList(send_email, blood_group):
  query = "SELECT * FROM DONOR WHERE BLOOD_GROUP=?"
  stmt = ibm_db.prepare(conn, query)
  ibm_db.bind_param(stmt,1,blood_group)
  ibm_db.execute(stmt)
  donors = ibm_db.fetch_assoc(stmt)
  donorList=[]
  if donors:
    while donors:
      donorList.append(donors)
      if send_email:
        sendMail(donors['EMAIL'], 'URGENT!!! Plasma Donation needed', '{} has requested for plasma of {} blood group. You can contact them at {} and {}'.format(isUser['NAME'],isUser['BLOOD_GROUP'],isUser['PHONE'], isUser['EMAIL']))
      donors = ibm_db.fetch_assoc(stmt)
  return donorList


@app.route("/recipient", methods=['GET','POST'])
def addRequest():
  if request.method == 'POST':
    query = "SELECT * FROM USERS WHERE Email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,session['email'])
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)

    insert_sql = "INSERT INTO RECIPIENT(NAME,EMAIL,BLOOD_GROUP,PINCODE) VALUES (?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, isUser['NAME'])
    ibm_db.bind_param(prep_stmt, 2, isUser['EMAIL'])
    ibm_db.bind_param(prep_stmt, 3, isUser['BLOOD_GROUP'])
    ibm_db.bind_param(prep_stmt, 4, isUser['PINCODE'])
    ibm_db.execute(prep_stmt)

    # sendMail(session['email'], 'Request for Plasma Received', 'Your Request has been added Successfully')
    donorList = getDonorsList(True, isUser['BLOOD_GROUP'])
  
    return render_template('recipient.html', name='Receiver Dashboard', request_for_plasma=True, count=len(donorList))
  
  query = "SELECT * FROM RECIPIENT WHERE Email=?"
  stmt = ibm_db.prepare(conn, query)
  ibm_db.bind_param(stmt,1,session['email'])
  ibm_db.execute(stmt)
  isUser = ibm_db.fetch_assoc(stmt)
  donorList=[]
  if isUser:
    donorList = getDonorsList(False, isUser['BLOOD_GROUP'])
  return render_template('recipient.html', name='Receiver Dashboard', request_for_plasma=isUser, count=len(donorList))

if __name__ == "__main__":
  app.run()