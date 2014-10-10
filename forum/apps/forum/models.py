# coding: utf-8
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib import admin
from string import join
from django.conf import settings

class UserProfile(models.Model):
    avatar = models.ImageField("Profile Pic", upload_to="images/", blank=True, null=True)
    posts = models.IntegerField(default=0)
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return unicode(self.user)

class Forum(models.Model):
    title = models.CharField(max_length=60)


    """Forum listings usually show the total number of posts as well as the author
     and subject of the latest post. That’s something we can easily add to our models"""
    def num_posts(self):
        return sum([t.num_posts() for t in self.thread_set.all()])

    def last_post(self):
        if self.thread_set.count():
            last = None
            for t in self.thread_set.all():
                l = t.last_post()
                if l:
                    if not last: last = l
                    elif l.created > last.created: last = l
            return last

    def __unicode__(self):
        return self.title

class Thread(models.Model):
    title = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    forum = models.ForeignKey(Forum)

    def __unicode__(self):
        return unicode(self.creator) + " - " + self.title

    def num_posts(self):
        return self.post_set.count()

    def num_replies(self):
        return self.post_set.count() - 1

    def last_post(self):
        if self.post_set.count():
            return self.post_set.order_by("created")[0]

class Post(models.Model):
    title = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    thread = models.ForeignKey(Thread)
    body = models.TextField(max_length=10000)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.creator, self.thread, self.title)

    def short(self):
        return u"%s - %s\n%s" % (self.creator, self.title, self.created.strftime("%b %d, %I:%M %p"))
    short.allow_tags = True

    def profile_data(self):
        p = self.creator.userprofile_set.all()[0]
        return p.posts, p.avatar


### Signals block#####
def create_user_profile(sender, **kwargs):
    """When creating a new user, make a profile for him or her."""
    u = kwargs["instance"]
    if not UserProfile.objects.filter(user=u):
        UserProfile(user=u).save()
        print "User %s is created" % (u,)

post_save.connect(create_user_profile, sender=User)



def new_post_created(sender, **kwargs):
        p = kwargs["instance"]
        print "New post created by %s" % p.creator
post_save.connect(new_post_created, sender=Post)















