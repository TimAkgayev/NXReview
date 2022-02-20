from django.db import models

# Create your models here.

class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.title


class Conflict(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.title


