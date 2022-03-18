from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime
from django.conf import settings

class User(AbstractUser):
    pass

AUCTION_CHOICES = (
    ("electronics", "electronics"),
    ("clothing", "clothing"),
    ("services", "services"),
    ("miscellaneous", "miscellaneous"),
)

class auctionListing(models.Model):
    itemName = models.CharField(max_length=255, null = False)
    madeBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    date = models.DateTimeField(auto_now_add=True) #Note that date and time is saved in UTC
    startingBid = models.FloatField(validators=[MinValueValidator(0.0)], null = False)
    description = models.TextField(default="", blank=True)
    imageURL = models.CharField(blank=True, default=f"{settings.STATIC_URL}auctions/images/noImageIcon.png", max_length=255)
    category = models.CharField(default="miscellaneous", max_length=255, choices=AUCTION_CHOICES)
    highestBidId = models.IntegerField(blank=True, null=True)
    open = models.BooleanField(default=True)
    usersWatching = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return self.itemName

class bid(models.Model):
    listing = models.ForeignKey(auctionListing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bidValue = models.FloatField(validators=[MinValueValidator(0.0)], null = False)
    date = models.DateTimeField(auto_now_add=True) #Note that date and time is saved in UTC

    def __str__(self):
        return f"Item: {self.listing} | Bid made by: {self.user} | Bid value: {self.bidValue} | Made on: {self.date}"

class comment(models.Model):
    listing = models.ForeignKey(auctionListing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(null = False)
    date = models.DateTimeField(auto_now_add=True) #Note that date and time is saved in UTC

    def __str__(self):
        return f"{self.comment} | Made by: {self.user} | on {self.listing}"
