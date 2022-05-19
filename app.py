from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azureproject.get_conn import get_conn
import os
import uuid

from requests import RequestException

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if not 'WEBSITE_HOSTNAME' in os.environ:
   # local development, where we'll use environment variables
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # production
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

with app.app_context():
    app.config.update(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=get_conn(),
    )

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# Create databases, if databases exists doesn't issue create
# For schema changes, run "flask db migrate"
from models import Restaurant, Review
db.create_all()
db.session.commit()

@app.route('/', methods=['GET'])
def index():
    from models import Restaurant
    print('Request for index page received')
    restaurants = Restaurant.query.all()    
    return render_template('index.html', restaurants=restaurants)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    return details(id,'')

def details(id, message):
    from models import Restaurant, Review
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant==id)
    account_url = get_account_url()
    image_path = account_url + "/" + os.environ['STORAGE_CONTAINER_NAME']
    return render_template('details.html', restaurant=restaurant, reviews=reviews, message=message, image_path=image_path)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    from models import Restaurant
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
        if (name == "" or description == "" ):
            raise RequestException()
    except (KeyError, RequestException):
        # Redisplay the restaurant entry form.
        return render_template('create_restaurant.html', 
            message='Restaurant not added. Include at least a restaurant name and description.')
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    from models import Review
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')   
        if (user_name == "" or rating == None):
            raise RequestException()
    except (KeyError, RequestException):
        # Redisplay the review form.
        from models import Restaurant
        restaurant = Restaurant.query.where(Restaurant.id == id).first()
        reviews = Review.query.where(Review.restaurant==id)
        return details(id, 'Review not added. Include at least a name and rating for review.')
    else:
        if request.files['reviewImage']:
            image_data = request.files['reviewImage']

            # Get size.
            size = len(image_data.read())
            image_data.seek(0)

            print("Original image name = " + image_data.filename)
            print("File size = " + str(size))

            if (size > 2048000):
                return details(id, 'Image too big, try again.')

            # Get account_url based on environment
            account_url = get_account_url()
            print("account_url = " + account_url)

            # Create client
            azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=azure_credential)

            # Get file name to use in database
            image_name = str(uuid.uuid4()) + ".png"
            
            # Create blob client
            blob_client = blob_service_client.get_blob_client(container=os.environ['STORAGE_CONTAINER_NAME'], blob=image_name)
            print("\nUploading to Azure Storage as blob:\n\t" + image_name)

            # Upload file
            blob_client.upload_blob(image_data)
        else:
            # No image for review
            image_name=None

        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        review.image_name = image_name
        db.session.add(review)
        db.session.commit()
                
    return redirect(url_for('details', id=id))        

@app.context_processor
def utility_processor():
    def star_rating(id):
        from models import Review
        reviews = Review.query.where(Review.restaurant==id)

        ratings = []
        review_count = 0;        
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = round(sum(ratings)/len(ratings), 2) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_account_url():
    # Create LOCAL_USE_AZURE_STORAGE environment variable to use Azure Storage locally. 
    if 'WEBSITE_HOSTNAME' in os.environ or ("LOCAL_USE_AZURE_STORAGE" in os.environ):
        print("Using Azure Storage.")
        return "https://%s.blob.core.windows.net" % os.environ['STORAGE_ACCOUNT_NAME']
    else:
        return os.environ['STORAGE_ACCOUNT_NAME']

if __name__ == '__main__':
   app.run()
