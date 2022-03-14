from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import markdown2
from random import randrange

from . import util

edited = None
new = None

class searchForm(forms.Form):
    search = forms.CharField(label="Search")

class newPageForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(widget=forms.Textarea, label="Markdown")

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

def randomPage(request):
    entries = util.list_entries()
    index = randrange(len(entries))
    return HttpResponseRedirect(f"../{entries[index]}")
                
def index(request):
    global new
    global edited

    alert = False
    message = "foo"
    if edited:
        alert = True
        message = f"Entry {edited} has been changed!"
        edited = None
    if new:
        alert = True
        message = f"A new entry has been created: {new}"
        new = None
    return render(request, "encyclopedia/index.html", {
        "alert": alert,
        "message": message,
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

def createPage(request):
    global new

    if request.method == "POST":
        form = newPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]
            if not util.get_entry(title):
                util.save_entry(title, markdown)
                new = title
                return HttpResponseRedirect(reverse("index"))
            else:
                #todo
                return HttpResponse("nah")
    return render(request, "encyclopedia/createPage.html", {
        "form": newPageForm(),
    })