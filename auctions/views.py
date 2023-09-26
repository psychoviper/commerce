from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.forms import CharField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .models import *

class Newform(forms.Form):
    title=forms.CharField(max_length=50, label="Title", widget=forms.TextInput(attrs={'class':"form-control"}))
    description= forms.CharField(max_length=200,label="Description", required=False, widget=forms.TextInput(attrs={'class':"form-control"}))
    bid=forms.DecimalField(decimal_places=2, max_digits=7, required=True, label="Starting bid", widget=forms.NumberInput(attrs={'class':"form-control"}))
    image=forms.ImageField(required=False,widget=forms.FileInput(attrs={'class':"form-control"}))


def index(request):
    li = Listings.objects.filter(active=True)
    if request.user.is_authenticated:
        num = 0
        try:
            users = User.objects.get(pk = request.user.id)
            users = users.watchlist_user.get(user=request.user).listings.all()
            num = len(users)
            return render(request, "auctions/index.html",{'lists':li, "list_of_categories": Category.objects.exclude(name="None"), 'number':num})

        except ObjectDoesNotExist:
            num = 0
            return render(request, "auctions/index.html",{'lists':li, "list_of_categories": Category.objects.exclude(name="None"), 'number':num})
    else:
        return render(request, "auctions/index.html",{'lists':li, "list_of_categories": Category.objects.exclude(name="None")})

    

def create(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            title=request.POST["title"]
            description= request.POST["description"]
            bid=float(request.POST["bid"])
            if len(request.FILES)!=0:
                image=request.FILES["image"]
            cat=request.POST["category"]
            category = Category.objects.get(name=cat)
            li = Listings(title=title,description=description,bid=bid,image=image,category=category, user=request.user)
            li.save()
            return HttpResponseRedirect(reverse("index"))
        form=Newform()
        return render(request, "auctions/create.html",{"form":form, 'categories':Category.objects.all()})
    else:
        return render(request, 'auctions/error.html',{'message':'Please Login to Create or Post Listings'})

def listing(request, list_id):
    listing = Listings.objects.get(pk=list_id)
    price=listing.bid
    if (listing.amount.filter(item=list_id).last()):
        price=listing.amount.filter(item=list_id).last().bid
    user = request.user.is_authenticated
    comments=listing.comments.all().order_by('id').reverse()
    if user != None:
            if listing.user==request.user:
                return render(request, "auctions/listing.html", {'listing':listing, 'user':request.user, 'price':price, 'bool':True, 'comments':comments})
            return render(request, "auctions/listing.html", {'listing':listing, 'user':request.user, 'price':price, 'comments':comments})
    
    return render(request, "auctions/listing.html", {'listing':listing})


def cdlisting(request, list_id):
    if request.user.is_authenticated:
        listing = Listings.objects.get(pk=list_id)
        user = User.objects.get(pk=request.user.id)
        if (listing.amount.filter(item=list_id).last() and user.money.filter(user=request.user)):
            price=listing.amount.filter(item=list_id).last().bid
            winner=listing.amount.filter(item=list_id).last().user
            if price==user.money.filter(user=request.user).last().bid:
                messages.success(request,"Congratulations! You won the Bid")
                return render(request, "auctions/cdlisting.html", {'listing':listing, 'price':price, 'winner':winner})
        return render(request, "auctions/cdlisting.html", {'listing':listing, 'winner':winner, 'price':price})
    else:
        return render(request, 'auctions/error.html',{'message':'Please Login to view the winner'})
        
@login_required
def add(request, listing_id):
    lists = Listings.objects.get(pk=listing_id)
    if(Watchlist.objects.filter(user=request.user)):
        Watchlist.objects.get(user=request.user).listings.add(lists)
    else:
        x=Watchlist(user=request.user)
        x.save()
        x.listings.add(lists)
    return HttpResponseRedirect(reverse("watch"))

@login_required
def remove(request, listing_id):
    lists = Listings.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.get(user=request.user)
    watchlist.listings.remove(lists)
    watchlist.save()
    return HttpResponseRedirect(reverse("watch"))

@login_required
def close(request, listing_id):
    lists = Listings.objects.get(pk=listing_id)
    lists.active=False
    lists.save()
    return HttpResponseRedirect(reverse("index"))

def closed(request):
    lists = Listings.objects.filter(active=False)
    return render(request, "auctions/closed.html", {'listing':lists})

@login_required
def watch(request):
    try:
        lists=Watchlist.objects.get(user=request.user).listings.all()
        return render(request, "auctions/watchlist.html", {'lists':lists})
    except ObjectDoesNotExist:
        return render(request, "auctions/watchlist.html")


def bidding(request, listing_id):
    if request.user.is_authenticated:
        if request.method=="POST":
            if request.POST['bid']:
                p=float(request.POST['bid'])
                lists = Listings.objects.get(pk=listing_id)
                if (p>float(lists.bid)):
                    if(lists.current_bid):
                        if p > float(lists.current_bid.bid):
                            bid = Bid(user=request.user, item=lists, bid=p)
                            bid.save()
                            lists.current_bid = bid
                            lists.save()
                            messages.success(request,"Successfully placed your Bid value.")
                            return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
                        else:
                            messages.error(request,"Your Bid value is smaller than Current bid.")
                            return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
                    else:
                        bid = Bid(user=request.user, item=lists, bid=p)
                        bid.save()
                        lists.current_bid = bid
                        lists.save()
                        messages.success(request,"Successfully placed your Bid value.")
                        return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
                else:
                    messages.error(request,"Your Bid value is smaller than the Starting Bid.")
                    return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
            else:
                messages.error(request,"Please enter Bid amount.")
                return HttpResponseRedirect(reverse('listing',args=(listing_id,)))
    else:
        return render(request, 'auctions/error.html',{'message':'Please Login to view the Product'})
    

def categories(request):
    return render(request, "auctions/categories.html", {
        "list_of_categories": Category.objects.exclude(name="None")
    })

def category(request, category_name):
    return render(request, "auctions/category.html", {
        "category": category_name,
        "items_in_category": Listings.objects.filter(category=Category.objects.get(name=category_name), active=True)
    })

@login_required
def comment(request, listing_name):
    if request.method == "POST":
        text = request.POST.get("comment")
        auction_listing = Listings.objects.get(name=listing_name)
        user_comment = Comment(user=request.user, comment=text)
        user_comment.save()
        auction_listing.comments.add(user_comment)
        auction_listing.save()
        message = "Successfully commented on listing!"
        return listing(request, listing_name, message=message)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request,"Invalid credentials")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

    
