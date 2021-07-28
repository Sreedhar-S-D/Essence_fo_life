from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from pymongo import MongoClient
from flask_mysqldb import MySQL
import smtplib 
from flask_uploads import UploadSet, configure_uploads, IMAGES
from datetime import datetime
from flask_mongoengine import MongoEngine
from regex.regex import Pattern
import yaml
import os
from config import *
import re


#pip install -U Werkzeug==0.16.0

error_message = ""

app = Flask(__name__)

app.secret_key = 'secret'

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = db['mysql_cursorclass']
app.config['UPLOADED_PHOTOS_DEST'] = db['uploaded_photos_dest']

mysql = MySQL(app)

client = MongoClient(db['mongo_uri'])
mongo = client['Essence-of-Life-main']

states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam','Bihar','Chhattisgarh','Delhi','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttarakhand','Uttar Pradesh','West Bengal']

organs = ['Bone marrow','Eye','Heart','Intestine','Kidney','Liver','Lung','Pancreas']

for i in range(len(organs)):
    data = mongo['organ'].find_one({'name': organs[i]})
    if(not data):
        mongo['organ'].insert_one({
            "name": organs[i],
            "value": 0,
            "post_death":0,
            "alive":0 , "donation":0,"post_death_donation":0,"alive_donation":0
        })
success = mongo['status'].find_one({'name': "success"})
if(not success):
        mongo['status'].insert_one({
            "name":"success",
            "value": 0,
        })

fail = mongo['status'].find_one({'name': "fail"})
if(not fail):
        mongo['status'].insert_one({
            "name": "fail",
            "value": 0,
        })

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('mainpage.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('adminpage.html')

@app.route('/AdminLogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        userid = request.form['userid']
        pswd = request.form['password']
        cur = mysql.connection.cursor()

        if userid == "admin@1234" and pswd == "admin@1234":
            return redirect(url_for('admin'))

        else:
            flash("Incorrect credentials !",'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/registerGovernment', methods=['GET', 'POST'])
def register_government():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        register = request.form
        govt_id  = register['govt_id']
        e_id = register['e_id']
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        state = register['state']
        pswd = register['pswd']
        re_enter_password = register['re_enter_password']

        if govt_id and e_id and state and pswd and re_enter_password:
            if len(govt_id)>=1:
                if len(pswd)>=3 and len(pswd)<26:
                    if pswd == re_enter_password :
                        cur.execute("insert into govt_login values(%s,%s,%s,%s,%s)",
                                    (govt_id, pswd, e_id, state, "o"))
                        mysql.connection.commit()
                        cur.close()
                        flash("The government is successfully registered !",'success')
                        return redirect(url_for('gdashboard'))

                    if not re.match(regex, e_id):
                        flash("Email is not in correct format")
                        
                    elif pswd != re_enter_password:
                        flash("Password doesn't match, Please re-enter the password!",'error')
                else:
                    flash("Invalid password !",'error')
            else:
                    flash("Please provide a valid username !",'error')
        else:
            flash("Please enter all the details !",'error')       
    return render_template('registerGovernment.html', availablestates = states)

@app.route('/GovernmentLogin', methods=['GET', 'POST'])
def govtlogin():
    if request.method == 'POST':
        userid = request.form['userid']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM govt_login WHERE login_id = %s", (userid,))

        if result > 0:
            data = cur.fetchone()
            guid = data['login_id']
            gpassword = data['pswd']

            session['gid'] = guid
        
            if gpassword==password_candidate:
                return redirect(url_for('gdashboard'))

            else:
                flash("Incorrect password !",'error')
                return render_template('loginGovtOfficial.html')

        else:
            flash('Username is wrong.','error')
            cur.close()
            return render_template('loginGovtOfficial.html')

    return render_template('loginGovtOfficial.html')

@app.route('/registerOrganisation', methods=['GET', 'POST'])
def register_organisation():
    if request.method == 'POST':
        register = request.form
        org_id = register['org_id']
        oname = register['oname']
        oemail = register['oemail']
        first_address = register['first_address']
        district = register['district']
        state = register['state']
        pincode = register['pincode']
        phone_num1 = register['phone_num1']
        phone_num2 = register['phone_num2']
        pswd = register['pswd']
        re_enter_password = register['re_enter_password']

        cur = mysql.connection.cursor()

        if org_id and oname and oemail and first_address and district and state and pincode and phone_num1 and phone_num2 and pswd and re_enter_password:
            head = register['head']
            if len(org_id)<11:
                if len(pincode)==6: 
                    if phone_num1>str(6000000000) and phone_num1<str(9999999999) and phone_num2>str(6000000000) and phone_num2<str(9999999999):
                        if len(pswd)>=3 and len(pswd)<26: 
                            if pswd == re_enter_password :
                                cur.execute("insert into organisation values(%s,%s,%s,%s,%s,%s,%s)",
                                            (org_id, oname, head, first_address, district, state, pincode))
                                cur.execute("insert into org_login values(%s,%s,%s,%s)", (org_id, pswd, oemail, "o"))
                                mysql.connection.commit()
                                cur.execute("insert into org_pnumber values(%s,%s)", (org_id,phone_num1))
                                cur.execute("insert into org_pnumber values(%s,%s)", (org_id,phone_num2))
                                mysql.connection.commit()
                                cur.close()
                                flash("The organisation is successfully registered !",'success')
                                return render_template('loginOrganisation.html')
                                
                            elif pswd != re_enter_password:
                                flash("Password doesn't match, Please re-enter the password!",'error')
                                redirect('/registerOrganisation')
                        else:
                            flash("Invalid Password !",'error')
                    else:
                        flash("Invalid phone number(s) !",'error')
                else:
                    flash("Incorrect pincode !",'error')
            else:
                flash("Incorrect Organisation ID !",'error')
        else:
            flash("Please enter all the details !",'error')       
    return render_template('registerOrganisation.html', states = states)

@app.route('/orequestPassword', methods=['GET','POST'])
def orequestpassword():
    if request.method == 'POST':
        req = request.form
        id = req['ID']
        cur = mysql.connection.cursor()
        res = cur.execute("select * from org_login where login_id = %s", (id,))
        if res>0:
            cur.execute("update org_login set opstatus = %s WHERE login_id = %s", ('r',id))
            mysql.connection.commit()
            flash("The request for password change has been sent and will get back to you soon!", "success")
        else:
            flash("ID doesn't exist!", "error")
    return render_template('osendrequest.html')

@app.route('/grequestPassword', methods=['GET','POST'])
def grequestpassword():
    if request.method == 'POST':
        req = request.form
        id = req['ID']
        print(email)
        cur = mysql.connection.cursor()
        res = cur.execute("select * from govt_login where login_id = %s", (id,))
        if res>0:
            cur.execute("update govt_login set pstatus = %s WHERE login_id = %s", ('r',id))
            mysql.connection.commit()
            flash("The request for password change has been sent and will get back to you soon!", "success")
        else:
            flash("ID doesn't exist!", "error") 
    return render_template('gsendrequest.html')

@app.route('/requests', methods=['GET','POST'])
def requests():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM org_login, organisation WHERE org_id=login_id and opstatus = %s", 'r')
    orequests = cur.fetchall()
    cur.execute("SELECT * FROM govt_login WHERE pstatus = %s", 'r')
    grequests = cur.fetchall()
    return render_template('pswdrequests.html', orequests = orequests, grequests = grequests)

@app.route('/ochangePassword', methods=['GET','POST'])
def ochangePassword():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM org_login")
    result = cur.fetchall()
    print(email)
    if request.method == 'POST':
        fpswddata = request.form
        orgid = fpswddata['orgID']
        eid = fpswddata['eID']
        ipswd = fpswddata['password']
        re_entered_password = fpswddata['repassword']
        
        if len(ipswd)>7 and len(ipswd)<26:
            if ipswd == re_entered_password :
                cur.execute("update org_login set pswd = %s where login_id = %s",(ipswd,orgid))
                cur.execute("update org_login set opstatus = %s where login_id = %s",("o",orgid))
                mysql.connection.commit()
                try:
                    s = smtplib.SMTP('smtp.gmail.com', 587)  
                    s.starttls() 
                    sender = ""
                    receiver = eid
                    sender_password = ""
                    s.login(email, password) 
                    TEXT = "Hello Organisation,\nAs per your request, the password for the organisation has been changed."+".\nRequest you to keep it safe and reach out to us if there are any discrepencies.\n\n\nThank you\n\nAdmin\nEssence of Life"
                    SUBJECT = "New password"
                    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                    s.sendmail("", receiver, message) 
                    s.quit() 
                except Exception as e:
                    global error_message
                    error_message = e
                    print(e)
                flash("Password updated and mail sent to the organisation!",'success')
                cur.close()
                return render_template('ochangePassword.html', values = result)
            else:
                flash("Password doesn't match !",'error')
        else:
            flash("Invalid Password !",'error')
    return render_template('ochangePassword.html', values = result)

@app.route('/gchangePassword', methods=['GET','POST'])
def gchangePassword():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM govt_login")
    result = cur.fetchall()
    print(email)
    if request.method == 'POST':
        fpswddata = request.form
        govtid = fpswddata['govtID']
        eid = fpswddata['eID']
        ipswd = fpswddata['password']
        re_entered_password = fpswddata['repassword']
        
        if len(ipswd)>7 and len(ipswd)<26:
            if ipswd == re_entered_password :
                cur.execute("update govt_login set pswd = %s where login_id = %s",(ipswd,govtid))
                cur.execute("update govt_login set pstatus = %s where login_id = %s",("o",govtid))
                mysql.connection.commit() 
                try:
                    s = smtplib.SMTP('smtp.gmail.com', 587)  
                    s.starttls() 
                    sender = ""
                    receiver = eid
                    sender_password = ""
                    s.login(email, password) 
                    TEXT = "Hello Government,\nAs per your request, the password for the organisation has been changed.\nThe new password is "+ipswd+".\nRequest you to keep it safe and reach out to us if there are any discrepencies.\n\n\nThank you\n\nAdmin\nEssence of Life"
                    SUBJECT = "New password"
                    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                    s.sendmail("", receiver, message) 
                    s.quit() 
                except Exception as e:
                    global error_message
                    error_message = e
                    print(e)
                flash("Password updated and mail sent to the registered government mail ID!",'success')
                cur.close()
                return render_template('gchangePassword.html', values = result)
            else:
                flash("Password doesn't match !",'error')
        else:
            flash("Invalid Password !",'error')
    return render_template('gchangePassword.html', values = result)

@app.route('/OrganisationLogin', methods=['GET', 'POST'])
def orglogin():
    if request.method == 'POST':
        userid = request.form['userid']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM org_login WHERE login_id = %s", (userid,))

        if result > 0:
            data = cur.fetchone()
            ouid = data['login_id']
            opassword = data['pswd']

            cur.execute("SELECT * FROM organisation WHERE org_id = %s",(ouid,))
            odetail = cur.fetchone()

            session['oid'] = ouid
            session['oname'] = odetail['oname']
            org = cur.fetchall()

            if opassword==password_candidate:
                return redirect(url_for('odashboard'))

            else:
                flash("Incorrect password !",'error')
                return render_template('loginOrganisation.html')

        else:
            flash('Username is wrong.','error')
            cur.close()
            return render_template('loginOrganisation.html')

    return render_template('loginOrganisation.html')

@app.route('/gdashboard', methods=['GET', 'POST'])
def gdashboard():
    return render_template('gdashboard.html')

@app.route('/odashboard', methods=['GET', 'POST'])
def odashboard():
    curid = session['oid']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM organisation WHERE org_id = %s",(curid,))
    org = cur.fetchall()
    return render_template('odashboard.html', org = org)

ALLOWED_EXTENSIONS = {'pdf'}
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/registerPatient', methods=['GET', 'POST'])
def register_patient():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM hospital")
    hospitals = cursor.fetchall()

    if request.method == 'POST':
        register = request.form
        patient_id = register['patient_id']
        pname = register['pname']
        phone_num = register['phone_num']
        organtype = register['organtype']
        hosp = register['hosp']
        oid = session['oid']
        file=request.files['preport']

        if patient_id and pname and phone_num and organtype and file:
            if len(patient_id)==12:
                first_address = register['first_address']
                district = register['district']
                state = register['state']
                dateOfBirth = register['dateOfBirth']
                gender = register['gender']
                bgroup = register['bgroup']
                if all(x.isalpha() or x.isspace() for x in pname):
                    if phone_num>str(600000000) and phone_num<str(9999999999):
                        f=file.filename 
                        prep = f.replace("'", "")
                        report = prep.replace(" ", "_") 
                        if report.lower().endswith(('.pdf')):
                            file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],report))
                            cur = mysql.connection.cursor()
                            cur.execute("insert into patient (patient_id, pname, dateOfBirth, phone_num, gender, bloodgroup, organ_required, first_address, district, state, ptorg_ID, preport) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (patient_id, pname, dateOfBirth, phone_num, gender, bgroup, organtype, first_address, district, state, oid, report))
                            mysql.connection.commit()
                        else:
                            flash('File not supported', 'error')
                            return redirect('/addFile')

                        if hosp == "other":
                            return redirect(url_for('registerHospital',pid=patient_id ,otype=organtype))
                        else:
                            cur.execute("SET foreign_key_checks = 0")
                            cur.execute("update patient set pthsp_ID = %s where patient_id = %s ",(hosp, patient_id))
                            print(hosp)
                            mysql.connection.commit()
                            cur.execute("SET foreign_key_checks = 1")
                            mysql.connection.commit()
                            return redirect(url_for('registerDoctor',pid=patient_id , hosp_id=hosp, otype=organtype))
                        cur.close()
                    else:
                        flash('Invalid phone number !', 'error')
                else:
                    flash('Name must have only alphabets !', 'error')
            else:
                flash('Invalid Aadhar ID !', 'error')
        else:
            flash('Please enter all the details !', 'error')

    return render_template('registerPatient.html', states = states, hospitals = hospitals)
    
@app.route('/registerDonor', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        register = request.form
        donor_id = register['donor_id']
        dname = register['dname']
        phone_num = register['phone_num']
        oid = session['oid']
        file=request.files['dreport']

        if donor_id and dname and phone_num and file:
            dateOfBirth = register['dateOfBirth']
            first_address = register['first_address']
            district = register['district']
            state = register['state']
            gender = register['gender']      
            bgroup = register['bgroup']
            donationtype = register['donationtype']
            expiry = register['expiry']
            if len(donor_id)==12:
                if all(x.isalpha() or x.isspace() for x in dname):
                    if phone_num>str(600000000) and phone_num<str(9999999999):
                        f=file.filename 
                        drep = f.replace("'", "")
                        report = drep.replace(" ", "_") 
                        if report.lower().endswith(('.pdf')):
                            file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],report))
                            cur = mysql.connection.cursor()
                            
                            cur.execute("insert into donor values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (donor_id, dname, dateOfBirth, phone_num, gender, bgroup, first_address, district, state, oid, report))
                            if expiry:
                                organtype = register['organtype']
                                i = organs.index(organtype)
                                cur.execute("insert into organ_available values(%s,%s,%s,%s,%s)",
                                    (donor_id, i+1, organtype, donationtype, expiry))
                                mysql.connection.commit()
                            else:
                                organtype = register['organtype2']
                                i = organs.index(organtype)
                                cur.execute("insert into organ_available(dnr_ID, organ_no, organtype, typeofdonation) values(%s,%s,%s,%s)",
                                    (donor_id, i+1, organtype, donationtype))
                                mysql.connection.commit()
                            print(organtype)
                            cur.close()
                            mongo['organ'].update({'name': organtype}, {'$inc': {'donation': 1}})
                            if donationtype=="Post-death":
                                mongo['organ'].update({'name': organtype}, {'$inc': {'post_death_donation': 1}})
                            if donationtype=="Alive":
                                mongo['organ'].update({'name': organtype}, {'$inc': {'alive_donation': 1}})

                            flash("Donor has been successfully registered!",'success')
                            return redirect(url_for('findPatient',did=donor_id ,otype=organtype))
                        else:
                            flash('File not supported', 'error')
                            return redirect('/addFile')
                    else:
                        flash('Invalid phone number !', 'error')
                else:
                    flash('Name must contain only alphabets !', 'error')
            else:
                flash('Invalid Aadhar ID !', 'error')
        else:
            flash('Please enter all the details !', 'error')

    return render_template('registerDonor.html', states = states)

@app.route('/registerHospital/<pid>/<otype>', methods=['GET', 'POST'])
def registerHospital(pid, otype):
    if request.method == 'POST':
        # fetch form data
        register = request.form
        hosp_id = register['hosp_id']
        hname = register['hname']
        first_address = register['first_address']
        district = register['district']
        state = register['state']
        pincode = register['pincode']
        phone_num1 = register['phone_num1']

        if hosp_id and hname and phone_num1 and first_address and district and state and pincode:
            head = register['head']
            phone_num2 = register['phone_num2']
            if phone_num1>str(6000000000) and phone_num1<str(9999999999):
                if len(pincode)==6:
                    cur = mysql.connection.cursor()
                    cur.execute("SET foreign_key_checks = 0")
                    cur.execute("update patient set pthsp_ID = %s where patient_id = %s ",(hosp_id, pid))
                    mysql.connection.commit()
                    cur.execute("SET foreign_key_checks = 1")
                    cur.execute("insert into hospital values(%s,%s,%s,%s,%s,%s,%s)",
                                (hosp_id, hname, head, first_address, district, state, pincode))
                    mysql.connection.commit()
                    cur.execute("insert into hosp_pnumber values(%s,%s)", (hosp_id,phone_num1))
                    cur.execute("insert into hosp_pnumber values(%s,%s)", (hosp_id,phone_num2))
                    mysql.connection.commit()
                    cur.close()
                    flash("The hospital is successfully registered !",'success')
                    return redirect(url_for('registerDoctor',pid=pid, hosp_id=hosp_id, otype=otype))
                else:
                    flash('Invalid pincode !', 'error')
            else:
                flash('Invalid phone number(s) !', 'error')
        else:
            flash('Please enter all the details !', 'error')

    return render_template('registerHospital.html', states = states)

@app.route('/registerDoctor/<pid>/<hosp_id>/<otype>', methods=['GET', 'POST'])
def registerDoctor(pid, hosp_id, otype):
    cur = mysql.connection.cursor()
    cur.execute("select * from doctor where dochosp_ID = %s ",(hosp_id,))
    doctors = cur.fetchall()
    if request.method == 'POST':
        # fetch form data
        register = request.form
        doc = register['doc']
        if doc == "other" :
            doctor_id = register['doctor_id']
            docname = register['docname']

            if doctor_id and docname:   
                phone_num = register['phone_num']
                gender = register['gender']
                cur = mysql.connection.cursor()
                cur.execute("SET foreign_key_checks = 0")
                cur.execute("update patient set ptdoc_ID = %s where patient_id = %s ",(doctor_id, pid))
                mysql.connection.commit()
                cur.execute("SET foreign_key_checks = 1")
                cur.execute("insert ignore into doctor values(%s,%s,%s,%s,%s)",
                            (doctor_id, docname, phone_num, gender, hosp_id))
                mysql.connection.commit()
                cur.close()
                flash("Patient has been successfully added!",'success')
            else:
                flash("Please enter all the details!",'error')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SET foreign_key_checks = 0")
            cur.execute("update patient set ptdoc_ID = %s where patient_id = %s ",(doc, pid))
            mysql.connection.commit()
            cur.execute("SET foreign_key_checks = 1")    
            flash("Patient has been successfully added!",'success')

        return redirect(url_for('findDonor',pid=pid ,orgtype=otype))

    return render_template('registerDoctor.html', doctors = doctors)

@app.route('/findDonor/<pid>/<orgtype>', methods=['GET', 'POST'])
def findDonor(pid,orgtype):
    cur = mysql.connection.cursor()
    cur.execute("select donor_id, dname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, dreport, expiry, organtype, state, typeofdonation from donor, organ_available where donor_id=dnr_id and organtype = %s and donor_ID NOT IN(select dnr_ID from transplantation) and typeofdonation = 'post-death' and expiry>current_timestamp order by state, expiry asc", (orgtype,))
    pddonors = cur.fetchall()            
    cur.execute("select donor_id, dname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, dreport, organtype, state, typeofdonation from donor, organ_available where donor_id=dnr_id and organtype = %s and donor_ID NOT IN(select dnr_ID from transplantation) and typeofdonation = 'alive' order by state, age", (orgtype,))
    adonors = cur.fetchall()  
    cur.close()
    return render_template("findDonor.html", pddonors=pddonors, adonors=adonors, patid = pid, show=True)

@app.route('/findPatient/<did>/<otype>', methods=['GET', 'POST'])
def findPatient(did, otype):  
    cur = mysql.connection.cursor()
    cur.execute("select patient_id, pname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, phone_num, state, preport, organ_required from patient where organ_required = %s and patient_ID NOT IN(select pnt_ID from transplantation) order by state, age", (otype,))
    patients=cur.fetchall()            
    cur.close()
    return render_template("findPatient.html",patients=patients, donid = did, show=True)

@app.route('/findDonor/<orgtype>', methods=['GET', 'POST'])
def findDonors(orgtype):
    cur = mysql.connection.cursor()
    cur.execute("select donor_id, dname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, dreport, expiry, organtype, state, typeofdonation from donor, organ_available where donor_id=dnr_id and organtype = %s and donor_ID NOT IN(select dnr_ID from transplantation) and typeofdonation = 'post-death' and expiry>current_timestamp order by state, expiry asc", (orgtype,))
    pddonors = cur.fetchall()            
    cur.execute("select donor_id, dname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, dreport, organtype, state, typeofdonation from donor, organ_available where donor_id=dnr_id and organtype = %s and donor_ID NOT IN(select dnr_ID from transplantation) and typeofdonation = 'alive' order by state, age", (orgtype,))
    adonors = cur.fetchall()  
    cur.close()
    return render_template("findDonor.html", pddonors=pddonors, adonors=adonors, show=False)

@app.route('/findPatient/<otype>', methods=['GET', 'POST'])
def findPatients(otype):  
    cur = mysql.connection.cursor()
    cur.execute("select patient_id, pname, TimeStampDiff(year,dateOfBirth,CurDate()) as age, gender, bloodgroup, phone_num, state, preport, organ_required from patient where organ_required = %s and patient_ID NOT IN(select pnt_ID from transplantation) order by state, age", (otype,))
    patients=cur.fetchall()            
    cur.close()
    return render_template("findPatient.html",patients=patients, show=False)

@app.route('/searchwotid', methods=['GET', 'POST'])
def searchwotid():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT organtype FROM organ_available order by organtype")
    organ = cursor.fetchall()
    if request.method == 'POST':
        otype = request.form['organtype']
        if request.form['searchfor'] == "donors":
            return redirect(url_for('findDonors', orgtype=otype))
        else:
            return redirect(url_for('findPatients', otype=otype))            
    return render_template('search.html',organs=organ, show=False)

@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT organtype FROM organ_available order by organtype")
    organ = cursor.fetchall()
    if request.method == 'POST':
        uid = request.form['userid']
        otype = request.form['organtype']

        if request.form['searchfor'] == "donors":
            result = cursor.execute("SELECT * FROM patient where patient_id=%s and organ_required = %s",(uid, otype))
            if result > 0 :
                return redirect(url_for('findDonor',pid=uid ,orgtype=otype))
            else:
                flash("Patient ID/corresponding organ is invalid!",'error')
                return render_template('search.html',organs=organ, show=True)
        else:
            result = cursor.execute("SELECT * FROM donor, organ_available where donor_id=dnr_id and donor_id=%s and organtype = %s",(uid,otype))
            if result > 0 :
                return redirect(url_for('findPatient',did=uid ,otype=otype))
            else:
                flash("Donor ID/corresponding organ is invalid!",'error')
                return render_template('search.html',organs=organ, show=True)              

    return render_template('search.html',organs=organ, show=True)

@app.route('/transplantation/', methods=['GET', 'POST'])
def transplantation():
    if request.method == 'POST':
        register = request.form
        donor_id = register['donor_id']
        patient_id = register['patient_id']
        trdate = register['date']
        trstatus = register['status']
        otype = register['organtype']
        cur = mysql.connection.cursor()
        r1 = cur.execute("select * from patient where organ_required = %s and patient_ID = %s", (otype,patient_id))
        r2 = cur.execute("select * from donor, organ_available where organtype = %s and donor_ID = %s", (otype,donor_id )) 
        val = cur.fetchone()

        if r1>0 and r2>0 :
            i = organs.index(otype)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO transplantation(trdate,trstatus,dnr_ID,organ_no,pnt_ID) values (%s,%s,%s,%s,%s)",(trdate,trstatus,donor_id,i+1,patient_id))
            donors=cur.fetchall() 
            mysql.connection.commit()          
            cur.close()
            mongo['organ'].update({'name': otype}, {'$inc': {'value': 1}})
            print(val['typeofdonation'])
            if val['typeofdonation']=="Post-death":
            	mongo['organ'].update({'name': otype}, {'$inc': {'post_death': 1}})    
            if val['typeofdonation']=="Alive":
            	mongo['organ'].update({'name':otype},{'$inc':{'alive':1}})
            if trstatus=="success":
                mongo['status'].update({'name':"success"},{'$inc':{'value':1}})
            if trstatus=="fail":
                mongo['status'].update({'name':"fail"},{'$inc':{'value':1}})
            flash("Transplantation details are added !",'success')
            return render_template("transplantation.html")
        else :
            flash("Wrong Patient ID/Donor ID for given organ !",'error')
            return render_template("transplantation.html")

    return render_template("transplantation.html")

@app.route('/analysis', methods=['GET'])
def data():
    d=mongo['organ'].find()
    data=[]
    status=[]
    success=mongo['status'].find_one({'name':"success"})
    fail=mongo['status'].find_one({'name':"fail"})
    total=success['value']+fail['value']
    total=total if total!=0 else 1
    status.append({'label':"success",'y':(success['value']*100)/total})
    status.append({'label':"failure",'y':(fail['value']*100)/(total)})
    dataJson = []
    for data in d:
        name = data['name']
        value = data['value']
        post_death = data['post_death']
        alive = data['alive']
        donation=data['donation']
        post_death_donation=data['post_death_donation']
        alive_donation=data['alive_donation']
        dataDict = {'name':name,'value':value,'post_death':post_death,'alive':alive,'donation':donation,'post_death_donation':post_death_donation,'alive_donation':alive_donation}
        dataJson.append(dataDict) 
    return render_template('graph.html',data=dataJson,status=status)

@app.route('/finddetails', methods=['GET', 'POST'])
def finddetails():
    if request.method == 'POST':
        find = request.form
        person = find['searchfor']
        perid = find['userid']
        button = find['but']
        if button == "SEARCH":
            return redirect(url_for('find', perid=perid, person=person))
    
    return render_template('finddetails.html', donor=False, patient=False, disp=False)

@app.route('/find/<perid>/<person>', methods=['GET', 'POST'])
def find(perid, person):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        xyz = request.form
        button = xyz['but']
        print(button)
        
        if button == "SEARCH":
            person = xyz['searchfor']
            perid = xyz['userid']
            return redirect(url_for('find', perid=perid, person=person))

        if button == "Delete Patient":
            cur.execute("delete from patient where patient_id = %s",(perid,))
            mysql.connection.commit()
            flash("Patient deleted successfully !",'success')
            return redirect(url_for('finddetails'))

        if button == "Delete Donor":
            cur.execute("delete from donor where donor_id = %s",(perid,))
            mysql.connection.commit() 
            flash("Donor deleted successfully !",'success')
            return redirect(url_for('finddetails'))

        if button == "Update":
            return redirect(url_for('update', perid=perid, person=person))
    
    if person == "donor":
        cur.execute("select * from donor, organ_available where donor_id=dnr_id and donor_id = %s",(perid,))
        donor=cur.fetchall()
        print(donor)
        return render_template('finddetails.html', a = donor, donor=True, patient=False, disp=True)

    elif person == "patient":
        cur.execute("select * from patient, hospital where pthsp_ID=hospital_id and patient_id = %s",(perid,))
        patient=cur.fetchall()
        print(patient)
        return render_template('finddetails.html', a = patient, donor=False, patient=True, disp=True)

@app.route('/update/<perid>/<person>', methods=['GET', 'POST'])
def update(perid, person):
    cur = mysql.connection.cursor()

    if person == "patient":
        pat = True
        don = False
        cur.execute("select * from patient where patient_id = %s",(perid,))
        values = cur.fetchall()
    else:
        don = True
        pat = False
        cur.execute("select * from donor where donor_id = %s",(perid,))
        values = cur.fetchall()

    if request.method == 'POST':
        req = request.form 
        file = request.files['report']

        f=file.filename 
        rep = f.replace("'", "")
        report = rep.replace(" ", "_") 
        if report.lower().endswith(('.pdf')):
            file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'],report))
            cur = mysql.connection.cursor()
            if person == "patient":
                cur.execute("update patient set preport = %s where patient_id = %s",(report, perid))
                mysql.connection.commit()
                flash("Report updated !", 'success')
                return redirect(url_for('find', perid=perid, person=person))
            else:
                cur.execute("update donor set dreport = %s where donor_id = %s",(report, perid))
                mysql.connection.commit()
                flash("Report updated !", 'success')
                return redirect(url_for('find', perid=perid, person=person))
        else:
            flash('File not supported', 'error')
            return redirect('/addFile')
        cur.close()

    return render_template('updatedetails.html', patient = pat, donor = don, values = values)

@app.route('/addFile',methods=['GET','POST'])
def addFile():
    cur = mysql.connection.cursor()
    cur.execute("select * from donor where donor_id = '109986701201'")
    res = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    '''if request.method == 'POST':
        return redirect(url_for('download', filename = res[0]['dreport']))'''

    return render_template("addFile.html", dres = res[0]['dreport'])

@app.route('/download/<filename>')
def download(filename):
   return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
