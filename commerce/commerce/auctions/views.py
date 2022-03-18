from django.contrib.auth import authenticate, login, logout, decorators
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from urllib.parse import urlencode

from .auctionForms import createListingForm, bidForm, closeBidForm, commentForm, addToWatchlistForm,listingCategories
from .models import User, auctionListing, bid, comment

class info:
    def __init__(self, listing):
        self.itemName = listing.itemName
        maxBid = bid.objects.filter(id=listing.highestBidId).first()
        if maxBid:
            self.maxBid = "{:.2f}".format(maxBid.bidValue)
        else:
            self.maxBid = None
        self.startingBid = "{:.2f}".format(listing.startingBid)
        self.imageURL = listing.imageURL
        self.date = listing.date
        self.listingId = listing.id
        self.user = listing.madeBy
        self.description = listing.description
        self.open = listing.open
        self.currUserIsHighestBidder = False

def index(request):
    itemAdded = False
    if request.method == "POST":
        category = request.POST.get("category")
        if category == "all":
            listings = auctionListing.objects.filter(open=True)
        else:
            listings = auctionListing.objects.filter(category=category, open=True)
    else:
        listings = auctionListing.objects.filter(open=True)
        category = "all"
        itemAdded = request.GET.get("added", False)
    consolidatedInfo = []
    for listing in listings[::-1]:
        listingInfo = info(listing)
        listingInfo.currUserIsHighestBidder = userIsHighestBidder(request, listing)
        consolidatedInfo.append(listingInfo)
    return render(request, "auctions/index.html",{
        "selectedCategory": category,
        "categories": listingCategories,
        "consolidatedInfo": consolidatedInfo,
        "itemAdded" : itemAdded
    })

def categories(request):
    return render(request, "auctions/categories.html",{
        "categories": listingCategories,
    })

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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

def createListing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        if request.method == "POST":
            form = createListingForm(request.POST)
            if form.is_valid():
                user = request.user
                itemName = form.cleaned_data["itemName"]
                startingBid = form.cleaned_data["startingBid"]
                description = form.cleaned_data["description"]
                category = form.cleaned_data["category"]
                if form.cleaned_data["imageURL"]:
                    imageURL = form.cleaned_data["imageURL"]
                else:
                    imageURL = f"{settings.STATIC_URL}auctions/images/noImageIcon.png"
                newListing = auctionListing(
                    itemName=itemName, 
                    startingBid=startingBid, 
                    madeBy=user, 
                    description=description, 
                    category=category,
                    imageURL=imageURL)
                newListing.save()
                baseURL = reverse("index")
                queryString = urlencode({"added": True})
                url = '{}?{}'.format(baseURL, queryString)
                return HttpResponseRedirect(url)
            else:
                return render(request, "auctions/createListing.html", {
                    "itemName": request.POST.get("itemName"),
                    "startingBid": request.POST.get("startingBid"),
                    "description": request.POST.get("description"),
                    "selectedCategory": request.POST.get("category"),
                    "imageURL": request.POST.get("imageURL"),
                    "categories": listingCategories
                })
        else:
            return render(request, "auctions/createListing.html", {
                "categories": listingCategories
            })

def userIsHighestBidder(request, listing):
    userIsHighestBidder = False
    if request.user.is_authenticated:
        highestBidder = bid.objects.filter(id=listing.highestBidId).first()
        if highestBidder:
            userIsHighestBidder = highestBidder.user.id == request.user.id
    return userIsHighestBidder

def inWatchList(request, listingId):
    if request.user.watchlist.filter(id=listingId).first():
        return True
    return False

def reqListing(request, listingId):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        else:
            message = None
            warnMessage = None
            isHighestBidder = False
            watchlist = inWatchList(request, listingId)
            if request.POST.get("action") == "bid":
                form = bidForm(request.POST)
                if form.is_valid():
                    listing = auctionListing.objects.filter(id=form.cleaned_data["listingId"]).first()
                    if request.user.id == listing.madeBy.id:
                        warnMessage = "You cannot bid on your own item"
                    else:
                        newBid = bid(
                            listing = listing,
                            user = request.user,
                            bidValue = form.cleaned_data["bidValue"],
                        )
                        newBid.save()
                        listing.highestBidId = newBid.id
                        listing.save()
                        isHighestBidder = True
                        message= "Bid successfully made"
                else:
                    listing = auctionListing.objects.filter(id=form.cleaned_data["listingId"]).first()
                    #Checks if the current user is the highest bidder, if the user is authenticated                   
                    warnMessage = "Please input a bid larger than the current highest bid"
            elif request.POST.get("action") == "close":
                form = closeBidForm(request.POST)
                if form.is_valid():
                    listing = auctionListing.objects.filter(id=form.cleaned_data["listingId"]).first()
                    listing.open = False
                    listing.save()
                    message = "Listing successfully closed"
            elif request.POST.get("action") == "comment":
                form = commentForm(request.POST)
                listing = auctionListing.objects.filter(id=listingId).first()
                if form.is_valid():
                    newComment = form.cleaned_data["comment"]
                    newComment = comment(
                        listing = listing,
                        user = request.user,
                        comment = newComment
                    )
                    newComment.save()
                else:
                    warnMessage = "Comment cannot be empty"
            elif request.POST.get("action") == "addRemoveToWatchlist":
                form = addToWatchlistForm(request.POST)
                if form.is_valid():
                    listing = auctionListing.objects.filter(id=form.cleaned_data["listingId"]).first()
                    if watchlist:
                        listing.usersWatching.remove(request.user)
                        message = "Successfully removed from Watchlist"
                        listing.save()
                        watchlist = False
                    else:
                        listing.usersWatching.add(request.user)
                        message = "Successfully added to Watchlist"
                        listing.save()
                        watchlist = True
                else:
                    warnMessage = "Failed to add to Watchlist"
                    print("barrr")
            comments = listing.comments.all()
            listingInfo = info(listing)
            return render(request, "auctions/listing.html", {
                "listing": listingInfo,
                "comments": comments,
                "message": message,
                "warnMessage": warnMessage,
                "userIsHighestBidder": isHighestBidder,
                "watchlist": watchlist,
            })

    listing = auctionListing.objects.filter(id=listingId).first()
    listingInfo = info(listing)
    if request.user.is_authenticated:
        watchlist = inWatchList(request, listingId)
    else:
        watchlist = False
    #Checks if the current user is the highest bidder, if the user is authenticated
    isHighestBidder = userIsHighestBidder(request, listing)
    comments = listing.comments.all()

    return render(request, "auctions/listing.html", {
        "userIsHighestBidder": isHighestBidder,
        "listing": listingInfo,
        "comments": comments,
        "watchlist": watchlist
    })

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        watchlistListings = request.user.watchlist.all()
        consolidatedInfo = []
        for listing in watchlistListings[::-1]:
            listingInfo = info(listing)
            listingInfo.currUserIsHighestBidder = userIsHighestBidder(request, listing)
            consolidatedInfo.append(listingInfo)
        return render(request, "auctions/watchlist.html",{
            "watchlistListings": consolidatedInfo
        })