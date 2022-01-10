from typing import Sized
from django.shortcuts import render, redirect
from .models import Topic
import xml.etree.ElementTree as ET
import difflib
from .forms import ConflictResolutionForm

# Create your views here.
def index(request):
    """Home page view"""
    
    #open XML file and check it against the DB
    #Merge any duplicate topics 
    
    

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
            cm = difflib.get_close_matches(topic.title, dbTitleList,cutoff=0.7)
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

    context = {'topics': Topic.objects.all()}
    return render(request, 'nxreview/index.html', context)
   
def conflicts(request):
    if request.method == "POST":
        #Go through each conflict item

        dbItems = Topic.objects.all()
        for key in request.POST:

            isDBObjFound = False
            #Find the conflict item in the database
            for obj in dbItems:
                if obj.title == key:
                    dbObject = obj
                    isDBObjFound = True

            if isDBObjFound == False:
                continue

            #Find both items in the XML
            xmlItems = openAndParseXML('Review.xml')
            duplicateXMLTopics = []
            for obj in xmlItems:
                if obj.title == key:
                    duplicateXMLTopics.append(obj)
            
            #Merge xml items
            mergedTopic = Topic()
            mergedTopic.title = key
            for obj in duplicateXMLTopics:
                mergedTopic.text += obj.text
                mergedTopic.text += "\n"

            #Update the database item with the merged one
            dbObject.delete()
            Topic.objects.create(title=mergedTopic.title, text=mergedTopic.text)

            return redirect('nxreview:index')

    else:
        return render(request, 'conflicts.html')



                
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




        

        
    
  