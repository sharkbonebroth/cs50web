from django.contrib import admin

from .models import User, bid, auctionListing, comment

# Register your models here.
admin.site.register(User)
admin.site.register(bid)
admin.site.register(auctionListing)
admin.site.register(comment)