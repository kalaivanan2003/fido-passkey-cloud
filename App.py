from flask import Flask, render_template, flash, request, session, send_file, redirect, jsonify
import sqlite3
import os as _os

# ── Database path (always next to App.py) ────────────────────────
DB_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'fidoclouddb.sqlite')

def get_db():
    """Return a new SQLite connection with WAL mode for concurrency."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    """
    Create all tables if they don't already exist.
    Called automatically at startup — safe to run multiple times.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS regtb (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            Name          TEXT    NOT NULL,
            Mobile        TEXT    NOT NULL,
            Email         TEXT    NOT NULL,
            Address       TEXT    NOT NULL,
            UserName      TEXT    NOT NULL UNIQUE,
            Password      TEXT    NOT NULL,
            Status        TEXT    NOT NULL DEFAULT 'waiting',
            Pubkey        TEXT    NOT NULL DEFAULT '',
            Prikey        TEXT    NOT NULL DEFAULT '',
            prikey1       TEXT    NOT NULL DEFAULT '',
            prikey2       TEXT    NOT NULL DEFAULT '',
            face_encoding TEXT
        );

        CREATE TABLE IF NOT EXISTS backuptb (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT    NOT NULL,
            Enckey   TEXT    NOT NULL,
            pubkey   TEXT    NOT NULL,
            prikey2  TEXT    NOT NULL,
            Qrcode   TEXT    NOT NULL,
            Hash1    TEXT    NOT NULL,
            Hash2    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS filetb (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            OwnerName TEXT    NOT NULL,
            FileInfo  TEXT    NOT NULL,
            FileName  TEXT    NOT NULL,
            Pukey     TEXT    NOT NULL,
            Pvkey     TEXT    NOT NULL,
            hash1     TEXT    NOT NULL,
            hash2     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS temptb (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT    NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    print(f"[DB] SQLite ready: {DB_PATH}")

# ── Auto-initialise DB on every startup ──────────────────────────
init_db()

from ecies.utils import generate_key
from ecies import encrypt, decrypt
import base64, os
import sys
import json
import numpy as np

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# Ensure required static upload folders exist
for _folder in ['static/Qrcode', 'static/upload', 'static/Encrypt', 'static/Decrypt']:
    _os.makedirs(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), _folder), exist_ok=True)


@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/ServerLogin")
def ServerLogin():
    return render_template('ServerLogin.html')


@app.route("/BackupServer")
def BackupServer():
    return render_template('BackupServer.html')


@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')


@app.route("/serverlogin", methods=['GET', 'POST'])
def serverlogin():
    if request.method == 'POST':
        if request.form['uname'] == 'server' and request.form['password'] == 'server':

            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb WHERE LOWER(status)='waiting'")
            data = cur.fetchall()
            cur.execute("SELECT * FROM regtb WHERE LOWER(status)!='waiting'")
            data1 = cur.fetchall()
            conn.close()
            return render_template('ServerHome.html', data=data, data1=data1)

        else:
            flash('Username or Password is Incorrect !')
            return render_template('ServerLogin.html')


@app.route("/ServerHome")
def ServerHome():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb WHERE LOWER(status)='waiting'")
    data = cur.fetchall()
    cur.execute("SELECT * FROM regtb WHERE LOWER(status)!='waiting'")
    data1 = cur.fetchall()
    conn.close()
    return render_template('ServerHome.html', data=data, data1=data1)


import hmac
import hashlib
import binascii


def create_sha256_signature(key, message):
    byte_key = binascii.unhexlify(key)
    message = message.encode()
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()


def xor_hex_strings(hex1, hex2):
    """Perform XOR operation between two hex string hashes."""
    # Convert hex strings to bytes
    bytes1 = bytes.fromhex(hex1)
    bytes2 = bytes.fromhex(hex2)

    # Perform XOR operation
    xor_result = bytes(a ^ b for a, b in zip(bytes1, bytes2))

    # Convert result back to hexadecimal
    return xor_result.hex()


@app.route("/Approved")
def Approved():
    uid   = request.args.get('lid')
    email = request.args.get('email')
    prkey = ""

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regtb WHERE id=?", (uid,))
    data = cursor.fetchone()
    if data:
        prkey = data[9]   # Prikey column

    secp_k   = generate_key()
    privhex1 = secp_k.to_hex()
    prikey2  = xor_hex_strings(prkey, privhex1)

    # ── DB UPDATE FIRST (so approval is never lost even if email fails) ──
    cursor.execute(
        "UPDATE regtb SET Status='awaiting backup server', prikey1=?, prikey2=? WHERE id=?",
        (privhex1, prikey2, uid))
    conn.commit()

    # ── Attempt email (non-fatal) ────────────────────────────────────────
    mail_ok = sendmail(email,
        "FIDO Cloud: Server has approved your registration.\n"
        "FIDOKEY: " + prikey2 + "\n"
        "Status: Awaiting Backup Server approval.")

    cursor.execute("SELECT * FROM regtb WHERE LOWER(status)='waiting'")
    data  = cursor.fetchall()
    cursor.execute("SELECT * FROM regtb WHERE LOWER(status)!='waiting'")
    data1 = cursor.fetchall()
    conn.close()

    if mail_ok:
        flash('User approved! FIDO key sent to their email.')
    else:
        flash('User approved! (Email notification failed — please notify the user manually.)')

    return render_template('ServerHome.html', data=data, data1=data1)


@app.route("/Reject")
def Reject():
    id    = request.args.get('lid')
    email = request.args.get('email')

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE regtb SET Status='reject' WHERE id=?", (id,))
    conn.commit()

    sendmail(email, "FIDO Cloud: Your registration request has been rejected.")

    cursor.execute("SELECT * FROM regtb WHERE LOWER(status)='waiting'")
    data  = cursor.fetchall()
    cursor.execute("SELECT * FROM regtb WHERE LOWER(status)!='waiting'")
    data1 = cursor.fetchall()
    conn.close()
    flash('User rejected.')

    return render_template('ServerHome.html', data=data, data1=data1)


@app.route('/SFileInfo')
def SFileInfo():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM filetb")
    data1 = cur.fetchall()
    conn.close()
    return render_template('SFileInfo.html', data=data1)


@app.route("/bslogin", methods=['GET', 'POST'])
def bslogin():
    if request.method == 'POST':
        if request.form['uname'] == 'server' and request.form['password'] == 'server':

            return BackupServerHome()

        else:
            flash('Username or Password is Incorrect !')
            return render_template('BackupServer.html')


@app.route("/BackupServerHome")
def BackupServerHome():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb WHERE LOWER(status)='awaiting backup server'")
    data = cur.fetchall()
    cur.execute("SELECT * FROM regtb WHERE LOWER(status)!='waiting'")
    data1 = cur.fetchall()
    conn.close()
    return render_template('BackupServerHome.html', data=data, data1=data1)

@app.route('/QrcodeInfo')
def QrcodeInfo():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM backuptb")
    data1 = cur.fetchall()
    conn.close()
    return render_template('QrcodeInfo.html', data=data1)



import hmac
import hashlib
import binascii


def create_sha256_signature(key, message):
    byte_key = binascii.unhexlify(key)
    message = message.encode()
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()


@app.route("/QrApproved")
def QrApproved():
    uid = request.args.get('lid')
    email = request.args.get('email')
    prkey1 = ""
    pupkey = ""
    uname = ""
    prkey2 = ""

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT  *  FROM  regtb where  id=?", (uid,))
    data = cursor.fetchone()
    if data:
        uname = data[5]
        pupkey = data[8]
        prkey1 = data[10]
        prkey2 = data[11]

    message = prkey1
    message_bytes = message.encode("utf-8")

    # ----------------------------------
    # 3. Encryption (using PUBLIC key)
    # ----------------------------------
    ciphertext = encrypt(pupkey, message_bytes)
    print("Encrypted (hex):", ciphertext.hex())
    Enckey = ciphertext.hex()

    Qrcodehstr = Enckey + "," + pupkey + "," + prkey2

    print(Qrcodehstr)

    import qrcode
    img = qrcode.make(str(prkey2))
    import random
    pn = random.randint(1111, 9999)
    img.save("static/Qrcode/" + str(pn) + ".png")
    Qrcode = str(pn) + ".png"
    print(Qrcode)

    cursor.execute("UPDATE regtb SET Status='approved' WHERE id=?", (uid,))
    conn.commit()

    cursor.execute("SELECT * FROM backuptb")
    data = cursor.fetchone()

    if data:
        cursor.execute("SELECT max(id) FROM backuptb")
        da = cursor.fetchone()
        if da:
            d = da[0]
            print(d)

        cursor.execute("SELECT * FROM backuptb WHERE id=?", (d,))
        data = cursor.fetchone()
        if data:
            hash1 = data[7]
            num1 = random.randrange(1111, 9999)
            hash2 = create_sha256_signature("E49756B4C8FAB4E48222A3E7F3B97CC3", str(num1))

            cursor.execute(
                "INSERT INTO backuptb (UserName, Enckey, pubkey, prikey2, Qrcode, Hash1, Hash2) VALUES (?,?,?,?,?,?,?)",
                (uname, Enckey, pupkey, prkey2, Qrcode, hash1, hash2))
            conn.commit()

    else:
        hash1 = '0'
        num1 = random.randrange(1111, 9999)
        hash2 = create_sha256_signature("E49756B4C8FAB4E48222A3E7F3B97CC3", str(num1))
        cursor.execute(
            "INSERT INTO backuptb (UserName, Enckey, pubkey, prikey2, Qrcode, Hash1, Hash2) VALUES (?,?,?,?,?,?,?)",
            (uname, Enckey, pupkey, prkey2, Qrcode, hash1, hash2))
        conn.commit()

    conn.close()

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr = email

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "FIDO Cloud  "

    # string to store the body of the mail
    body = "Login Qrcode"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = Qrcode
    attachment = open("./static/Qrcode/" + filename, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "kkvz xxke jmeb pcyb")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

    flash("Qrcode Created Send to User..!")

    return BackupServerHome()


@app.route('/OwnerFileUpload')
def OwnerFileUpload():
    return render_template('OwnerFileUpload.html', oname=session['oname'])


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        uname = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        secp_k = generate_key()
        privhex = secp_k.to_hex()
        pubhex = secp_k.public_key.format(True).hex()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regtb WHERE username=?", (username,))
        data = cursor.fetchone()
        if data is None:
            cursor.execute(
                "INSERT INTO regtb (Name, Mobile, Email, Address, UserName, Password, Status, Pubkey, Prikey, prikey1, prikey2) "
                "VALUES (?,?,?,?,?,?,'waiting',?,?,?,?)",
                (uname, mobile, email, address, username, password, pubhex, privhex, '', ''))
            conn.commit()
            conn.close()

            session['reg_uname'] = username
            flash('Record Saved! Please capture your face now.')
            return redirect('/face-capture')
        else:
            flash('Already Register This  UserName!')
            return render_template('NewUser.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':

        username = request.form['uname']
        password = request.form['password']

        session['uname'] = request.form['uname']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regtb WHERE username=? AND Password=?", (username, password))
        data = cursor.fetchone()
        conn.close()
        if data is None:
            flash('Username or Password is wrong')
            return render_template('UserLogin.html')

        else:

            Status = data[7].lower() if data[7] else ''
            session['fidokey'] = data[11]
            # print(lkey)

            if Status == "waiting":

                flash('Waiting For Server Approved!')
                return render_template('UserLogin.html')

            elif Status == "awaiting backup server":
                flash('Awaiting Backup Server...!')
                return render_template('UserLogin.html')

            else:
                return redirect('/face-verify')


def loginvales1():
    uname = session['uname']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regtb WHERE username=?", (uname,))
    data = cursor.fetchone()
    conn.close()

    if data:
        Email = data[3]
        Phone = data[2]


    else:
        return 'Incorrect username / password !'

    return uname, Email, Phone


@app.route("/facelogin")
def facelogin():
    uname = session['uname']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM temptb WHERE username=?", (uname,))
    data = cursor.fetchone()
    conn.close()
    if data is None:

        flash('Face Verification Failed..!')
        return render_template('UserLogin.html')


    else:

        return render_template('FIDOVerify.html')


@app.route("/vlogin", methods=['GET', 'POST'])
def vlogin():
    if request.method == 'POST':

        loginkey = request.form['loginkey']

        if loginkey == session['fidokey']:

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backuptb WHERE username=?", (session['uname'],))
            data = cursor.fetchone()
            conn.close()

            if data:
                session["Enckey"] = data[2]
                session["pubkey"] = data[3]
                session["prikey2"] = data[4]

            return redirect('/qr-scan')


        else:

            flash('FIDO Key Verification Failed..!')
            return render_template('FIDOVerify.html')


# ──────────────────────────────────────────────────────────────
# FACE CAPTURE (Registration) — Browser-based
# ──────────────────────────────────────────────────────────────

@app.route('/face-capture')
def face_capture():
    return render_template('FaceCapture.html')


@app.route('/save-face', methods=['POST'])
def save_face():
    data = request.get_json()
    descriptor = data.get('descriptor')
    uname = session.get('reg_uname')
    if not uname or not descriptor:
        return jsonify({'success': False, 'message': 'Invalid session. Please register again.'})
    encoding_json = json.dumps(descriptor)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE regtb SET face_encoding=? WHERE username=?", (encoding_json, uname))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ──────────────────────────────────────────────────────────────
# FACE VERIFY (Login) — Browser-based
# ──────────────────────────────────────────────────────────────

@app.route('/face-verify')
def face_verify_page():
    return render_template('FaceVerify.html')


@app.route('/verify-face', methods=['POST'])
def verify_face():
    data = request.get_json()
    descriptor = data.get('descriptor')
    image_data = data.get('image', '')
    uname = session.get('uname')
    if not uname or not descriptor:
        return jsonify({'success': False, 'message': 'Session expired. Please login again.'})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT face_encoding, Email FROM regtb WHERE username=?", (uname,))
    row = cursor.fetchone()
    if not row or not row[0]:
        conn.close()
        return jsonify({'success': False, 'message': 'Face not enrolled. Please contact admin.'})
    stored = np.array(json.loads(row[0]))
    new_enc = np.array(descriptor)
    distance = float(np.linalg.norm(stored - new_enc))
    if distance < 0.6:
        cursor.execute("INSERT INTO temptb (UserName) VALUES (?)", (uname,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    else:
        email = row[1] if row else None
        if email and image_data:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders
                img_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
                alert_path = 'static/out.jpg'
                with open(alert_path, 'wb') as f:
                    f.write(img_bytes)
                fromaddr = "projectmailm@gmail.com"
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = email
                msg['Subject'] = "Illegal Access Tracing"
                msg.attach(MIMEText("Unknown user attempted to access your account.", 'plain'))
                with open(alert_path, 'rb') as f:
                    p = MIMEBase('application', 'octet-stream')
                    p.set_payload(f.read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', 'attachment; filename=suspicious_face.jpg')
                msg.attach(p)
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(fromaddr, "kkvz xxke jmeb pcyb")
                s.sendmail(fromaddr, email, msg.as_string())
                s.quit()
            except Exception as e:
                print("Alert email error:", e)
        return jsonify({'success': False, 'message': 'Face verification failed. Access denied.'})


# ──────────────────────────────────────────────────────────────
# QR CODE SCAN (Login Step 4) — Browser-based
# ──────────────────────────────────────────────────────────────

@app.route('/qr-scan')
def qr_scan():
    return render_template('QrScan.html')


@app.route('/verify-qr', methods=['POST'])
def verify_qr():
    data = request.get_json()
    qr_data = data.get('qrData', '').strip()
    if not qr_data:
        return jsonify({'success': False, 'message': 'No QR data received.'})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backuptb WHERE prikey2=?", (qr_data,))
    data1 = cursor.fetchone()
    conn.close()
    if data1:
        Enckey = data1[2]
        pubkey = data1[3]
        prikey2 = data1[4]
        if (prikey2 == session.get('prikey2') and
                pubkey == session.get('pubkey') and
                Enckey == session.get('Enckey')):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'QR code does not match your account.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid QR code.'})


@app.route("/UserHome")
def UserHome():
    uname = session['uname']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb WHERE UserName=?", (uname,))
    data = cur.fetchall()
    conn.close()
    return render_template('UserHome.html', data=data)


@app.route('/UserFileUpload')
def UserFileUpload():
    if 'uname' not in session:
        flash('Session expired. Please log in again.')
        return redirect('/UserLogin')
    return render_template('UserFileUpload.html', uname=session['uname'])


@app.route("/usfileupload", methods=['GET', 'POST'])
def usfileupload():
    if 'uname' not in session:
        flash('Session expired. Please log in again.')
        return redirect('/UserLogin')

    if request.method == 'POST':
        oname = session['uname']
        info  = request.form.get('info', '')
        file  = request.files.get('file')

        if not file or file.filename == '':
            flash('No file selected.')
            return render_template('UserFileUpload.html', uname=oname)

        import random
        fnew     = random.randint(111, 999)
        savename = str(fnew) + file.filename

        APP_DIR       = _os.path.dirname(_os.path.abspath(__file__))
        upload_path   = _os.path.join(APP_DIR, "static", "upload",  savename)
        encrypt_path  = _os.path.join(APP_DIR, "static", "Encrypt", savename)

        try:
            file.save(upload_path)

            secp_k  = generate_key()
            privhex = secp_k.to_hex()
            pubhex  = secp_k.public_key.format(True).hex()

            with open(upload_path, "rb") as f:
                raw_b64 = base64.b64encode(f.read())

            encrypted_bytes = encrypt(pubhex, raw_b64)

            with open(encrypt_path, "wb") as ef:
                ef.write(base64.b64encode(encrypted_bytes))

            conn   = get_db()
            cursor = conn.cursor()

            # Hash chaining for tamper detection
            cursor.execute("SELECT hash2 FROM filetb ORDER BY id DESC LIMIT 1")
            last_row = cursor.fetchone()
            hash1 = last_row[0] if last_row else '0'

            num1  = random.randrange(1111, 9999)
            hash2 = create_sha256_signature("E49756B4C8FAB4E48222A3E7F3B97CC3", str(num1))

            cursor.execute(
                "INSERT INTO filetb (OwnerName, FileInfo, FileName, Pukey, Pvkey, hash1, hash2) "
                "VALUES (?,?,?,?,?,?,?)",
                (oname, info, savename, pubhex, privhex, hash1, hash2))
            conn.commit()
            conn.close()

            flash('File uploaded and encrypted successfully!')
            return render_template('UserFileUpload.html', pkey=privhex, oname=oname)

        except Exception as e:
            print("[usfileupload ERROR]", e)
            flash(f'Upload failed: {str(e)}')
            return render_template('UserFileUpload.html', uname=oname)

    return render_template('UserFileUpload.html', uname=session.get('uname', ''))


@app.route('/UserFileInfo')
def UserFileInfo():
    if 'uname' not in session:
        flash('Session expired. Please log in again.')
        return redirect('/UserLogin')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM filetb WHERE OwnerName=?", (session['uname'],))
    data1 = cur.fetchall()
    conn.close()
    return render_template('UserFileInfo.html', data=data1)


@app.route("/UDownload")
def UDownload():
    if 'uname' not in session:
        flash('Session expired. Please log in again.')
        return redirect('/UserLogin')
    uname = session['uname']
    return render_template('UDownload.html')


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searc = request.form['searc']

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM filetb WHERE OwnerName=? AND (FileInfo LIKE ? OR FileName LIKE ?)",
            (session['uname'], f'%{searc}%', f'%{searc}%'))
        data1 = cur.fetchall()
        conn.close()
        return render_template('UDownload.html', data=data1)


@app.route("/Decryptkey")
def Decryptkey():
    if 'uname' not in session:
        flash('Session expired. Please log in again.')
        return redirect('/UserLogin')

    ufid = request.args.get('ufid')
    session["ufid"] = ufid

    uname  = session['uname']
    email  = ""
    prikey = ""
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regtb WHERE username=?", (uname,))
    data1 = cursor.fetchone()
    if data1:
        email = data1[3]

    cursor.execute("SELECT * FROM filetb WHERE id=?", (ufid,))
    data = cursor.fetchone()
    conn.close()
    if data:
        prikey = data[5]

    session['prikey'] = prikey

    mailmsg = "File Id: " + str(ufid) + "\nDecrypt Key: " + prikey

    sendmail(email, mailmsg)

    flash("Decrypt key sent to your registered email!")

    return render_template('DecryptFile.html')


@app.route("/fdecrypt", methods=['GET', 'POST'])
def fdecrypt():
    if request.method == 'POST':

        prkey = request.form.get('prkey', '').strip()
        stored_prikey = session.get('prikey', '')
        ufid = session.get('ufid')

        if not ufid:
            flash('Session expired. Please request the decrypt key again.')
            return render_template('DecryptFile.html')

        if prkey != stored_prikey:
            flash('Decrypt Key Verification Failed..!')
            return render_template('DecryptFile.html')

        # Fetch file record
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filetb WHERE id=?", (ufid,))
        data = cursor.fetchone()
        conn.close()

        if not data:
            flash('File record not found!')
            return render_template('DecryptFile.html')

        privhex = data[5]
        fname   = data[3]

        APP_DIR      = _os.path.dirname(_os.path.abspath(__file__))
        enc_path     = _os.path.join(APP_DIR, 'static', 'Encrypt', fname)
        dec_path     = _os.path.join(APP_DIR, 'static', 'Decrypt', fname)

        # Check encrypted file exists
        if not _os.path.exists(enc_path):
            flash(f'Encrypted file not found on server: {fname}')
            return render_template('DecryptFile.html')

        try:
            with open(enc_path, "rb") as f:
                encrypted_b64 = f.read()

            # Undo outer base64 wrapper applied during upload
            encrypted_bytes = base64.b64decode(encrypted_b64)

            # ECIES decrypt — gives back the inner base64-encoded original file bytes
            decrypted_b64 = decrypt(privhex, encrypted_bytes)

            # Undo inner base64 to recover original file content
            original_bytes = base64.b64decode(decrypted_b64)

            with open(dec_path, "wb") as f:
                f.write(original_bytes)

            return send_file(dec_path, as_attachment=True,
                             download_name=fname)

        except Exception as e:
            print("[fdecrypt ERROR]", e)
            flash(f'Decryption failed: {str(e)}')
            return render_template('DecryptFile.html')


def sendmail(Mailid, message):
    """Send email. Returns True on success, False on failure (never raises)."""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        fromaddr = "projectmailm@gmail.com"
        msg = MIMEMultipart()
        msg['From']    = fromaddr
        msg['To']      = Mailid
        msg['Subject'] = "FIDO Cloud Authentication - Alert"
        msg.attach(MIMEText(message, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        s.starttls()
        s.login(fromaddr, "kkvz xxke jmeb pcyb")
        s.sendmail(fromaddr, Mailid, msg.as_string())
        s.quit()
        print(f"[MAIL] Sent to {Mailid}")
        return True
    except Exception as e:
        print(f"[MAIL ERROR] Could not send to {Mailid}: {e}")
        return False


if __name__ == '__main__':
    _ssl_cert = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ssl', 'cert.pem')
    _ssl_key  = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ssl', 'key.pem')

    if _os.path.exists(_ssl_cert) and _os.path.exists(_ssl_key):
        print("[SSL] Certificate found — starting HTTPS on port 5000")
        print("      Access: https://YOUR-EC2-IP:5000")
        print("      (Accept the browser's self-signed cert warning, then camera will work)")
        app.run(host='0.0.0.0', port=5000, debug=False,
                ssl_context=(_ssl_cert, _ssl_key))
    else:
        print("[SSL] No certificate found — starting plain HTTP (camera blocked on remote URLs)")
        print("      To enable HTTPS: run  bash generate_ssl.sh  then restart")
        app.run(host='0.0.0.0', port=5000, debug=True)
