import hashlib
import sqlite3


def adduser(user_id, role, login, password):

    sqlite_file = 'waste_management.db'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    hash_name = 'sha256'
    salt = 'ssdirf993lksiqb4'
    iterations = 100000
    dk = hashlib.pbkdf2_hmac(hash_name, bytearray(password, 'ascii'), bytearray(salt, 'ascii'), iterations)

    c.execute('''INSERT INTO users(user_id, role, login, password)
                 VALUES(?,?,?,?)''', (user_id, role, login, str(dk)))

    conn.commit()
    conn.close()

    return 0


