""" This module contains the backend logic for the Item Catalog project """

from flask import Flask, render_template, url_for, request, redirect, \
    jsonify, make_response, flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from catalog_db_service import CatalogDbService
from functools import wraps
import random
import string
import json
import httplib2
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']

service = CatalogDbService()


# Helpers

def get_logged_in_user():
    """
        Utility function to retrieve the currently logged in user
    """
    return service.get_user_by_id(login_session['user_id'])


# Login/logout

@app.route('/login')
def login():
    """
        Generates a random CSRF token and then renders the login page
    """
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


@app.route('/logout')
def logout():
    """
        Logs the user out of the application
    """
    if login_session['provider'] == 'facebook':
        fbdisconnect()
        del login_session['facebook_id']

    if login_session['provider'] == 'google':
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']

    return redirect(url_for('show_categories'))


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
        Handles user login if the user selected Facebook
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?' \
          'grant_type=fb_exchange_token&client_id=%s&client_secret=%s' \
          '&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s' \
          '&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s' \
          '&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = service.get_user_id_by_email(login_session['email'])
    if not user_id:
        user_id = service.create_user_by_session(login_session=login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
        Handles user logout if the user used the Facebook API to login
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % \
          (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
        Handles user login if the user selected Google Sign In
    """
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists
    user_id = service.get_user_id_by_email(data["email"])
    if not user_id:
        user_id = service.create_user_by_session(login_session=login_session)
    login_session['user_id'] = user_id

    return "Login Successful"


@app.route('/gdisconnect')
def gdisconnect():
    """
        Handles user logout if the user used the Google Sign In API to login
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Application

@app.route('/')
@app.route('/catalog')
def show_categories():
    """
        Shows all categories to the user as well as latest 5 items
    """
    categories = service.get_categories()
    latest_items = service.get_latest_items()

    return render_template("categories.html", categories=categories,
                           items=latest_items)


@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def show_category(category_id):
    """
        Shows all items within a user selected category
    """
    categories = service.get_categories()
    category = service.get_category_by_id(category_id)
    category_items = service.get_items_by_category_id(category_id)
    return render_template("category.html", categories=categories,
                           items=category_items, category=category)


@app.route('/catalog/<int:category_id>/items/<int:item_id>')
def show_category_item(category_id, item_id):
    """
        Shows details about a specific user selected item
    """
    category = service.get_category_by_id(category_id)
    item = service.get_item_by_id(item_id)

    # Check if user is logged in
    if 'username' in login_session:
        user = get_logged_in_user()
    else:
        user = None

    return render_template("category_item.html", item=item,
                           category_name=category.name, creator=item.user,
                           user=user)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def edit_category_item(category_id, item_id):
    """
        Allow the creator to edit the item's details
    """
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    categories = service.get_categories()
    item = service.get_item_by_id(item_id)

    # Check if user is the item creator
    if item.user.id != login_session['user_id']:
        return redirect('/login')

    if request.method == 'POST':
        # Process form data
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        service.update_item(item)

        return redirect(
            url_for('show_category_item', category_id=item.category_id,
                    item_id=item.id))
    else:  # GET
        return render_template("edit_category_item.html", item=item,
                               categories=categories)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def delete_category_item(category_id, item_id):
    """
        Allow the creator to delete the item
    """
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    item = service.get_item_by_id(item_id)

    # Check if user is the item creator
    if item.user.id != login_session['user_id']:
        return redirect('/login')

    if request.method == 'POST':
        # Delete the item
        service.delete_item_by_id(item.id)
        return redirect(
            url_for('show_category', category_id=item.category_id))
    else:  # GET
        return render_template("delete_category_item.html", item=item,
                               category_name=item.category.name)


@app.route('/catalog/addItem', methods=['GET', 'POST'])
def add_category_item():
    """
        Allow the user to create a new item
    """
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    categories = service.get_categories()

    if request.method == 'POST':
        # Process form data
        if request.form['name'] and request.form['description']:
            service.create_item(name=request.form['name'],
                                description=request.form['description'],
                                category_id=request.form['category'],
                                user_id=login_session['user_id'])
        return redirect(
            url_for('show_categories'))
    else:  # GET
        return render_template("add_category_item.html", categories=categories)


# JSON

@app.route('/catalog/JSON')
def show_categories_json():
    """
        Return the JSON for all of the categories
    """
    categories = service.get_categories()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/catalog/<int:category_id>/JSON')
@app.route('/catalog/<int:category_id>/items/JSON')
def show_category_json(category_id):
    """
        Return the JSON for all of the items within a selected category
    """
    items = service.get_items_by_category_id(category_id)
    return jsonify(items=[item.serialize for item in items])


@app.route('/catalog/<int:category_id>/items/<int:item_id>/JSON')
def show_category_item_json(category_id, item_id):
    """
        Return the JSON for a specified item
    """
    item = service.get_item_by_id(item_id)
    return jsonify(item=[item.serialize])


if __name__ == "__main__":
    app.debug = True
    app.secret_key = "super_secret_key"
    app.run(host='0.0.0.0', port=5000)
