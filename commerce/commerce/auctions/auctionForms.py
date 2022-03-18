from django import forms
from .models import auctionListing, bid

listingCategories = ["electronics", "clothing", "services", "miscellaneous"]

class createListingForm(forms.Form):
    itemName = forms.CharField(max_length=255)
    startingBid = forms.FloatField()
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'name':'description', 'rows':3}))
    category = forms.CharField()
    imageURL = forms.CharField(required=False)

    def clean(self):
        cleanedData = super().clean()
        startingBid = cleanedData.get("startingBid")
        itemName = cleanedData.get("itemName")
        category = cleanedData.get("category")
        if startingBid == None:
            print("a")
            raise forms.ValidationError("PLease input an expected price")
        if startingBid < 0:
            print("b")
            raise forms.ValidationError("Expected price cannot be less than zero")
        if itemName == None:
            print("c")
            raise forms.ValidationError("PLease input an item name")
        if len(itemName) > 255:
            print("d")
            raise forms.ValidationError("Item name is too long")
        if category not in listingCategories:
            print("e")
            raise forms.ValidationError("Invalid category")

class bidForm(forms.Form):
    bidValue = forms.FloatField()
    listingId = forms.IntegerField()

    def clean(self):
        cleanedData = super().clean()
        bidValue = cleanedData.get("bidValue")
        listingId = cleanedData.get("listingId")
        #Checks if item exists
        item = auctionListing.objects.filter(id=listingId).first()
        if item:
            highestBid = bid.objects.filter(id=item.highestBidId).first()
            if highestBid:
                minBid = highestBid.bidValue
                if bidValue <= minBid:
                    print("invalid bid: not high enough")
                    raise forms.ValidationError("invalid bid: not high enough")
            else:
                minBid = item.startingBid
                if bidValue < minBid:
                    print("invalid bid: not high enough")
                    raise forms.ValidationError("invalid bid: not high enough")
        else:
            print("Cannot bid: item does not exist")
            raise forms.ValidationError("Cannot bid: item does not exist")

class closeBidForm(forms.Form):
    listingId = forms.IntegerField()

    def clean(self):
        cleanedData = super().clean()
        listingId = cleanedData.get("listingId")
        #Checks if item exists
        item = auctionListing.objects.filter(id=listingId).first()
        if not item:
            print("Cannot close: item does not exist")
            raise forms.ValidationError("Cannot close: item does not exist")

class commentForm(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea())

class addToWatchlistForm(closeBidForm):
    pass
