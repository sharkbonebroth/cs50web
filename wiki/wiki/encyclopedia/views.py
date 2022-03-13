from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import markdown2
import regex as re

from . import util

class searchForm(forms.Form):
    search = forms.CharField(label="Search")

def reqSearch(request):
    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            searchQuery = form.cleaned_data["search"]
            filtered = []
            entries = util.list_entries()
            for entry in entries:
                if searchQuery.lower() in entry.lower():
                    filtered.append(entry)
            if len(filtered) == 1:
                return HttpResponseRedirect(f"../{filtered[0]}")
            else:
                return render(request, "encyclopedia/results.html", {
                    "empty" : len(filtered) == 0,
                    "entries": filtered,
                    "form": searchForm()
                })                
                
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": searchForm()
    })

def reqEntry(request, entryName):
    requestedEntry = util.get_entry(entryName)
    if requestedEntry is None:
        data = "404 Not Found"
    else:
        data = markdown2.markdown(requestedEntry)
    return render(request, "encyclopedia/entryPage.html", {
        "entryName": entryName,
        "HTML": data,
        "form": searchForm()
    })