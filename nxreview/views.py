from typing import Sized
from django.shortcuts import render
from .models import Topic, Conflict
import xml.etree.ElementTree as ET
from xml.dom import minidom
import difflib
from .forms import ConflictResolutionForm

def index(request):
    #Parse xml files to produce a list of all tags
    xmlTopicList = openAndParseXML('Review.xml')

    Topic.objects.all().delete()

    #Go through the tag list and add it to the Topic database list
    for xmlTopic in xmlTopicList:
        topic = Topic()
        topic.title = xmlTopic.title
        topic.text = xmlTopic.text
        topic.save()

    syntax_file = open("Syntax.txt", 'r')
    sf_lines = syntax_file.readlines()

    #remove all the superflous tags used for classification
    topicList = Topic.objects.all()
    for t in topicList: 
        for sf_line in sf_lines:
            t.text = t.text.replace(sf_line.rstrip(), "")

    context = {'topics': topicList}
    return render(request, 'nxreview/index.html', context)

    
def quiz(request):
    context = {'topics': Topic.objects.all()}
    return render(request, 'nxreview/quiz.html', context)

def important(request):
    importantTopicList = []
    syntax_file = open("Syntax.txt", 'r')
    sf_lines = syntax_file.readlines()

    for t in Topic.objects.all():
        if t.text.find('[important]') != -1:
            for sf_line in sf_lines:
                t.text = t.text.replace(sf_line.rstrip(), "")
            importantTopicList.append(t)

    context = {'topics': importantTopicList}
    return render (request, 'nxreview/important.html', context)

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


 