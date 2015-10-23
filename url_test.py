from flask import Flask, redirect, request, render_template, make_response
import json
import requests
import stripe
import os

stripe.api_key = "sk_test_hzmKNeyNVEbyi1BWiTRwRHMe"
app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/', methods=['GET', 'POST'])
def sub():
    if request.method == 'GET':
        return render_template("test.html", email=request.args.get('email'))
    else:
        print("sub!")
        customer = stripe.Customer.create(
            source=request.form['stripeToken'],  # obtained from Stripe.js
            plan="test_plan",
            metadata={
                'birthday': request.form['birthday'],
            },
            email=request.form['email']
        )
        customer.subscriptions.create(plan="test_plan")
        return redirect("http://www.example.com/done", code=302)


@app.route('/stripe', methods=['POST'])
def stripe_hook():
    event_json = request.get_json()
    obj = event_json['data']['object']
    if event_json['type'] == "invoice.payment_succeeded":
        customer = stripe.Customer.retrieve(obj['customer'])
        print("send discount", customer.email)
    return "", 200


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
