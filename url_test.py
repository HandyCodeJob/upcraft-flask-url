from flask import Flask, redirect, request, render_template, make_response
import requests
import stripe
import os

stripe.api_key = "sk_test_hzmKNeyNVEbyi1BWiTRwRHMe"
app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/', methods=['GET', 'POST'])
def sub():
    print(request)
    if request.method == 'GET':
        return render_template("test.html", email=request.args.get('email'))
    else:
        print(request.form)
        customer = stripe.Customer.create(
            source=request.form['stripeToken'],  # obtained from Stripe.js
            plan="test_plan",
            metadata={
                'birthday': request.form['birthday'],
            },
            email=request.form['email']
        )
        print(customer)
        """
        data = {
            "customer": {
                "id": customer.stripe_id,
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
        print(data)
        shopify = requests.put(url, params=data)
        """
        customer.subscriptions.create(plan="test_plan")

        return redirect("http://www.example.com/done", code=302)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
