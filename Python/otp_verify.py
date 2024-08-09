import math
import random
import smtplib
import time

def generate_otp():
    nums = "0123456789"
    otp = "".join(random.choices(nums, k=6))
    return otp

def send_otp(emailid):
    otp = generate_otp()
    msg = f"Your OTP is {otp}. This OTP is valid for only 1 minute."
    
    #Email credentials and settings
    sender_email = 'Your gmail account'  #Replace with your email
    sender_password = 'app password'       #Replace with your app password
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    #Send OTP email
    s = smtplib.SMTP(smtp_server, smtp_port)
    s.starttls()
    s.login(sender_email, sender_password)
    s.sendmail(sender_email, emailid, msg)
    s.quit()
    
    #Record OTP time
    return otp, time.time()

def validate_otp(input_otp, generated_otp, gen_time):
    expiry_time = 60 
    if input_otp == generated_otp:
        if time.time() - gen_time <= expiry_time:
            return True, "OTP verified Successfully..!"
        else:
            return False, "Your OTP has expired. A new OTP has been sent."
    else:
        return False, "Invalid OTP. Please check and try again."

emailid = input("Enter your email: ")
otp, gen_time = send_otp(emailid)

while True:
    user_input_otp = input("Enter Your OTP: ")
    is_valid, message = validate_otp(user_input_otp, otp, gen_time)
    
    if is_valid:
        print("OTP Verified Successfully!")
        break
    else:
        print(message)
        if "expired" in message:
            otp, gen_time = send_otp(emailid)
