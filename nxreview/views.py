from typing import Sized
from django.shortcuts import render, redirect
from .models import Topic
import xml.etree.ElementTree as ET
import difflib
from .forms import ConflictResolutionForm

# Create your views here.
def index(request):
    """Home page view"""

    #check DB Size
    dbSize = len(Topic.objects.all())
    if dbSize == 0: 
        topicList = openAndParseXML('Review.xml')

        #check each topic to see if it exists in the database
        topicConflicts = [] 
        closeMatchMap = {}
        for topic in topicList:
            #extract titles in the existing database
            db = Topic.objects.all()
            dbTitleList = []
            for dbitem in db:
                dbTitleList.append(dbitem.title)

            #find any close matches between topic and existing titles
            cm = difflib.get_close_matches(topic.title, dbTitleList)
            if len(cm) > 0:
                #add conflicts to list for review
                closeMatchMap[len(topicConflicts)] = cm
                topicConflicts.append(topic.title)
                
            else:
                #no conflicts, insert into DB
                Topic.objects.create(title=topic.title, text=topic.text)

        #send page to render either the conflict view or the homepage
        if topicConflicts != 0:
            context = {'conflictTopicList':topicConflicts, 'closeMatchMap':closeMatchMap}
            return render(request, 'nxreview/conflicts.html', context)
        else:
            return redirect('nxreview:index')  
    return render(request, 'nxreview/index.html')
   
def conflicts(request):
    if request.method == "POST":
        form = ConflictResolutionForm(request.POST)
        if form.is_valid():
            val = form.cleaned_data.get("btn")
    else:
        form = ConflictResolutionForm()
        return render(request, 'conflicts.html',{'form':form})



                
def openAndParseXML(xmlfile):
    tr = ET.parse(xmlfile)
    rt = tr.getroot()
    #Generate a Topic list out of the parsed file
    topicList = []
    for child in rt:
        t = Topic()
        t.title = child.tag
        t.text = child.text
        topicList.append(t)
    return topicList




        

        
    
  