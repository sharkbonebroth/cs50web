from re import T
from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import markdown2
from random import randrange

from . import util

edited = False
new = None
warn = None

class searchForm(forms.Form):
    search = forms.CharField(label="Search")

class newPageForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(widget=forms.Textarea, label="markdown")

class editPageForm(forms.Form):
    markdown = forms.CharField(widget=forms.Textarea, label="markdown")
        

def reqSearch(request):
    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            searchQuery = form.cleaned_data["search"]
            filtered = []
            entries = util.list_entries()
            for entry in entries:
                if searchQuery.lower() == entry.lower():
                    return HttpResponseRedirect(f"../{entry}")
                if searchQuery.lower() in entry.lower():
                    filtered.append(entry)
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
    global warn

    alert = False
    giveWarning = False
    message = "foo"
    if new:
        alert = True
        message = f"A new entry has been created: {new}"
        new = None
    if warn:
        giveWarning = True
        message = f"Cannot edit entry: entry {warn} does not exist"
        warn = None
    return render(request, "encyclopedia/index.html", {
        "warn": giveWarning,
        "alert": alert,
        "message": message,
        "entries": util.list_entries(),
        "form": searchForm()
    })

def reqEntry(request, entryName):
    global edited

    displayEditedNoti = edited
    requestedEntry = util.get_entry(entryName)
    if requestedEntry is None:
        return render(request, "encyclopedia/errorPage.html")
    else:
        data = markdown2.markdown(requestedEntry)
        edited = False
    return render(request, "encyclopedia/entryPage.html", {
        "displayEditedNoti": displayEditedNoti,
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
                util.save_entry(title, bytes(markdown,'utf8'))
                new = title
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "encyclopedia/createPage.html", {
                    "form": newPageForm(),
                    "warn": True,
                    "title": title,
                })
    return render(request, "encyclopedia/createPage.html", {
        "form": newPageForm(),
    })

def editPage(request, entryName):
    global edited
    global warn

    if request.method == "POST":
        print("bar")
        form = editPageForm(request.POST)
        if form.is_valid():
            markdown = form.cleaned_data["markdown"]
            util.save_entry(entryName, bytes(markdown,'utf8'))
            edited = True
            return HttpResponseRedirect(reverse("reqEntry", args=[entryName]))
    markdownContent = util.get_entry(entryName)
    if not markdownContent:
        warn = entryName
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "encyclopedia/editPage.html", {
            "initial": markdownContent,
            "entryName": entryName,
        })