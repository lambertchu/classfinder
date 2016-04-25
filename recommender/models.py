from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save


class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    major1 = models.CharField(max_length=10)
    major2 = models.CharField(max_length=10)
    semester = models.IntegerField()
    classes = JSONField()

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username


class CompleteEnrollmentData(models.Model):
    identifier = models.IntegerField(blank=True, primary_key=True)
    major1 = models.TextField(blank=True, null=True)
    major2 = models.TextField(blank=True, null=True)
    minor1 = models.TextField(blank=True, null=True)
    minor2 = models.TextField(blank=True, null=True)
    term = models.TextField(blank=True, null=True)
    term_number = models.IntegerField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'complete_enrollment_data'


class SharedClassesByMajor(models.Model):
    major = models.TextField(blank=True, primary_key=True)
    matrix = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'shared_classes_by_major'


class SubjectInfo(models.Model):
    subject = models.TextField(blank=True, primary_key=True)
    title = models.TextField(blank=True, null=True)
    prereqs = models.TextField(blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    optional = models.TextField(blank=True, null=True)
    instructors = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)  # This field type is a guess.
    term1 = models.IntegerField(blank=True, null=True)
    term2 = models.IntegerField(blank=True, null=True)
    term3 = models.IntegerField(blank=True, null=True)
    term4 = models.IntegerField(blank=True, null=True)
    term5 = models.IntegerField(blank=True, null=True)
    term6 = models.IntegerField(blank=True, null=True)
    term7 = models.IntegerField(blank=True, null=True)
    term8 = models.IntegerField(blank=True, null=True)
    term9 = models.IntegerField(blank=True, null=True)
    term10 = models.IntegerField(blank=True, null=True)
    term11 = models.IntegerField(blank=True, null=True)
    term12 = models.IntegerField(blank=True, null=True)
    term13 = models.IntegerField(blank=True, null=True)
    term14 = models.IntegerField(blank=True, null=True)
    term15 = models.IntegerField(blank=True, null=True)
    term16 = models.IntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subject_info'
