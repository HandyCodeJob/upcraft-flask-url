from flask import Flask, redirect, request
import requests
import stripe
import os

stripe.api_key = "sk_test_hzmKNeyNVEbyi1BWiTRwRHMe"
app = Flask(__name__)


@app.route('/')
def hello():
    return redirect("http://www.example.com", code=302)


@app.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        customer = stripe.Customer.create(
            source=request.form['stripeToken'],  # obtained from Stripe.js
            plan="test_plan",
            metadata=request.form['birthday'],
            email=request.form['email']
        )
        data = {
            "customer": {
                "id": request.form['id'],
                "metafields": [
                    {
                        "key": "Premium",
                        "value": 1,
                        "value_type": "integer",
                        "namespace": "global",
                    }
                ],
            },
        }
        shopify = requests.put(url, params=data)
        print(customer, shopify)

        return redirect("http://www.example.com/done", code=302)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
