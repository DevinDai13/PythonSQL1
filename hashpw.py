# First import the pbkdf2_hmac function from the hashlib module
import hashlib


def getpassword(password):
    hash_name = 'sha256'
    salt = 'ssdirf993lksiqb4'
    iterations = 100000
    dk = hashlib.pbkdf2_hmac(hash_name, bytearray(password, 'ascii'), bytearray(salt, 'ascii'), iterations)
    return dk


def main():
    print('password hash....')
    password = input('Enter password: ')
    print(getpassword(password))
    return 0

if __name__ == '__main__':
    main()