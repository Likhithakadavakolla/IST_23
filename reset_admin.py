from werkzeug.security import generate_password_hash
import sqlite3, os

db_path = os.path.join('instance', 'edureach.db')
email = 'edureachtech@gmail.com'      # admin email to reset/create
new_pw = 'qazwsxedc'                   # new password

h = generate_password_hash(new_pw)
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute(
    "UPDATE student SET password_hash=?, is_admin=1, email_verified=1 "
    "WHERE lower(email)=lower(?)",
    (h, email),
)
if cur.rowcount == 0:
    cur.execute(
        "INSERT INTO student (name,email,class_level,password_hash,email_verified,is_admin) "
        "VALUES (?,?,?,?,1,1)",
        ('Administrator', email, 'admin', h),
    )
con.commit()
con.close()
print('Admin password reset/created for:', email)
