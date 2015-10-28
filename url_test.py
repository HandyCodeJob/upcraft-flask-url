from flask import Flask, redirect, request, render_template
import shopify
import requests
import re
import stripe
import os

STRIPE_API_SECRET_KEY = os.environ['STRIPE_API_SECRET_KEY']
STRIPE_API_PUBLIC_KEY = os.environ['STRIPE_API_PUBLIC_KEY']
SHOPIFY_API_KEY = os.environ['SHOPIFY_API_KEY']
SHOPIFY_PASSWORD = os.environ['SHOPIFY_PASSWORD']
URL = "https://%s:%s@upcraft-club.myshopify.com/admin" % (SHOPIFY_API_KEY,
                                                          SHOPIFY_PASSWORD)
nginx_line= """        rewrite "(?i)/%s/%s" http://upcraftclub.com/cart/%i:1?ref=%s#_l_1r ;\n"""
nginx_conf = """server {
        listen       80 default_server;
        server_name dev.handycodejob.com;
%s        rewrite "^/?$" http://upcraftclub.com/#_l_1r ;
}"""

stores = [
    'stitchdsm',
    'shop_another',
    'blah',
]


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

@app.route('/', methods=['GET', 'POST'])
def get_product():
    if request.method == GET:
        return ""
    else:
        product_url = request.form['url']

def get_nginx(urls, stores=stores):
    """Given an list of urls (or product handels) this will return the proper
    nginx config to have each of the stores to have each product"""
    product_ids = []
    lines = ''
    for product_url in urls:
        if product_url.startswith("http"):
            product = product_url.split('/')[-1]
        else:
            product = product_url
            product_url = "http://upcraftclub.com/products/%s" % product
        resp = requests.get(product_url)
        product_regex = re.search(r'"variants":\[{"id":(?P<id>\d+),"title', resp.text)
        product_id = int(product_regex.group('id'))
        lines += "        #%s: %i\n" % (product, product_id,)
        product_ids.append(product_id)
        for store in stores:
            line = nginx_line % (store, product, product_id, store,)
            lines += line
    nginx_out = nginx_conf % lines
    print(nginx_out)


def get_nginx_capture(urls, stores=stores):
    """Given an list of urls (or product handels) this will return the proper
    nginx config to have each of the stores to have each product"""
    product_ids = []
    lines = ''
    for product_url in urls:
        if product_url.startswith("http"):
            product = product_url.split('/')[-1]
        else:
            product = product_url
            product_url = "http://upcraftclub.com/products/%s" % product
        resp = requests.get(product_url)
        product_regex = re.search(r'"variants":\[{"id":(?P<id>\d+),"title', resp.text)
        product_id = int(product_regex.group('id'))
        lines += """        rewrite "(?i)/([\-\w]+)/%s" http://upcraftclub.com/cart/%i:1?ref=$1#_l_1r ;\n""" % (product, product_id,)
    nginx_out = nginx_conf % lines
    print(nginx_out)



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
