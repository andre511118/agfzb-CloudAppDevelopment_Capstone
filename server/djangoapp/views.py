from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, CarMake, CarModel, DealerReview
# from .restapis import related methods
from .restapis import get_request, get_dealers_from_cf
from .restapis import get_dealer_reviews_from_cf

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}

        state = request.GET.get("st")
        dealerId = request.GET.get("dealerId")
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/05e48284-5bc5-4a3a-8ec9-8f61b149b2e1/dealership-package/get-dealership"

        try:
            if state:
                dealerships = get_dealers_from_cf(url, st=state)
            elif dealerId:
                dealerships = get_dealers_from_cf(url, dealerId=dealerId)
            else:
                dealerships = get_dealers_from_cf(url)
        except Exception as e:
            # Handle the error and set dealerships to an empty list or display an error message
            dealerships = []
            context["error"] = f"An error occurred while fetching dealerships: {e}"

        context["dealership_list"] = dealerships
        print(context["dealership_list"])

        return render(request, "djangoapp/index.html", context=context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/05e48284-5bc5-4a3a-8ec9-8f61b149b2e1/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
    
        review_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/05e48284-5bc5-4a3a-8ec9-8f61b149b2e1/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        print(reviews)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):

def add_review(request, dealer_id):
    if request.method == "GET":
        # Retrieve the dealer for which we are adding a review (You can customize this based on your models)
        context = {}
        dealer_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/05e48284-5bc5-4a3a-8ec9-8f61b149b2e1/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            review = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = username
            review["dealership"] = id
            review["id"] = id
            review["review"] = request.POST["content"]
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    review["purchase"] = True
            review["purchase_date"] = request.POST["purchasedate"]           
            review["car_model"] = car.name
            payload = {}
            payload["review"] = review
            review_post_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/05e48284-5bc5-4a3a-8ec9-8f61b149b2e1/dealership-package/post-review"

            post_request(review_post_url, payload, id=id)
    return redirect("djangoapp:dealer_details", id=id)

