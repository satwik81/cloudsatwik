from flask import Flask, request, render_template
import random
import string

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def generate_password():
    if request.method == 'POST':
        pass_len = int(request.form['pass_len'])
        lowercase_letters = string.ascii_lowercase
        uppercase_letters = string.ascii_uppercase
        digits = string.digits
        special_symbols = "!@#$%^&*()?"

        # Ensure that the password contains at least one character from each category
        password = random.choice(lowercase_letters) + random.choice(uppercase_letters) + random.choice(
            digits) + random.choice(special_symbols)

        # Select remaining characters randomly
        for _ in range(pass_len - 4):
            password += random.choice(lowercase_letters + uppercase_letters + digits + special_symbols)

        # Shuffle the password to ensure randomness
        password_list = list(password)
        random.shuffle(password_list)
        p = ''.join(password_list)

        return f"The generated password is: {p}"

    return render_template('password_form.html')


if __name__ == '__main__':
    app.run(debug=True)
