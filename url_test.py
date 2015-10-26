from flask import Flask, redirect, request, render_template
import shopify
import stripe
import os

STRIPE_API_SECRET_KEY = os.environ['STRIPE_API_SECRET_KEY']
STRIPE_API_PUBLIC_KEY = os.environ['STRIPE_API_PUBLIC_KEY']
SHOPIFY_API_KEY = os.environ['SHOPIFY_API_KEY']
SHOPIFY_PASSWORD = os.environ['SHOPIFY_PASSWORD']
URL = "https://%s:%s@upcraft-club.myshopify.com/admin" % (SHOPIFY_API_KEY,
                                                          SHOPIFY_PASSWORD)

stripe.api_key = STRIPE_API_SECRET_KEY
shopify.ShopifyResource.set_site(URL)


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/', methods=['GET', 'POST'])
def sub():
    if request.method == 'GET':
        return render_template("test.html", email=request.args.get('email'),
                               STRIPE_API_PUBLIC_KEY=STRIPE_API_PUBLIC_KEY)
    else:
        print("sub!")
        customer = stripe.Customer.create(
            source=request.form['stripeToken'],  # obtained from Stripe.js
            plan="test_plan",
            metadata={
                'birthday': request.form['birthday'],
                'craft-type': request.form['craft-type'],
            },
            email=request.form['email']
        )
        customer.subscriptions.create(plan="test_plan")
        cust = get_customer(request.form['email'])
        resp = add_tag(cust, 'Premium')
        print('customer', customer, 'updated', resp)
        return redirect("http://www.example.com/done", code=302)


@app.route('/stripe', methods=['POST'])
def stripe_hook():
    event_json = request.get_json()
    obj = event_json['data']['object']
    if event_json['type'] == "customer.subscription.created":
        customer = stripe.Customer.retrieve(obj['customer'])
        print("User subbed: ", customer.email)
    return "", 200


def get_customer(email):
    """From and email, retrive customer obj from shopify"""
    query = shopify.Customer.search(query='email:' + email)
    for cust in query:
        if cust.attributes['email'] == email:
            cust_id = cust.attributes['id']
    cust = shopify.Customer().find(cust_id)
    return cust


def add_tag(customer, tag='Premium'):
    """Add a given tag to a customer, then return the result of .save()"""
    tags = customer.attributes['tags']
    if tags:
        tags += ', %s' % tag
    else:
        tags = tag
    customer.attributes.update({'tags': tags})
    return customer.save()


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
