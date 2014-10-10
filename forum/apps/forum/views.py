from django.http import HttpResponseRedirect, HttpResponse
from django.template import  RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from PIL import Image as PImage
from os.path import join as pjoin
from .models import Forum, Thread, Post, UserProfile
from .forms import ProfileForm
from django.utils.encoding import smart_str

def main(request):

    """Main listing."""
    context = RequestContext(request)
    forums = Forum.objects.all()
    return render_to_response("forum/list.html", dict(forums=forums, user=request.user), context)

def mk_paginator(request, items, num_items):
    """Create and return a paginator."""
    paginator = Paginator(items, num_items)
    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        items = paginator.page(page)
    except (InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)
    return items


def forum(request, pk):
    context = RequestContext(request)
    """Listing of threads in a forum."""
    threads = Thread.objects.filter(forum=pk).order_by("-created")
    threads = mk_paginator(request, threads, 20)
    context_dict = {'pk':pk, 'threads':threads}
    return render_to_response("forum/forum.html",context_dict, context)


def thread(request, pk):
    """Listing of posts in a thread."""
    context = RequestContext(request)
    posts = Post.objects.filter(thread=pk).order_by("created")
    posts = mk_paginator(request, posts, 15)
    t = Thread.objects.get(pk=pk)
    title = t.title
    forum_pk = t.forum.pk
    context_dict = {'pk':pk, 'posts': posts, 'title': title, 'forum_pk': forum_pk}
    return render_to_response("forum/thread.html", context_dict, context)



def post(request, ptype, pk):
    """we also need to add a way to post replies and new threads.
    I'll use the same template for both and call it post.html and
    the method names will be: post() to show the form
    and new_thread() and reply() to submit;
    urls will be: /forum/post/(new_thread|reply)/{id}/
    and /forum/new_thread/{id}/ and /forum/reply/{id}/."""
    """Display a post form."""
    context = RequestContext(request)

    action = reverse("forum:%s" % ptype, args=[pk])
    if ptype == "new_thread":
        title = "Start New Topic"
        subject = ''
    elif ptype == "reply":
        title = "Reply"
        subject = "Re: " + Thread.objects.get(pk=pk).title
    context_dict = {'subject':subject, 'action': action, 'title':title}

    return render_to_response("forum/post.html", context_dict, context)

def reply(request, pk):
    """Reply to a thread."""
    context = RequestContext(request)

    p = request.POST
    if p["body"]:
        thread = Thread.objects.get(pk=pk)
        Post.objects.create(thread=thread, title=p["subject"], body=p["body"],
            creator=request.user)
        increment_post_counter(request)

    return HttpResponseRedirect(reverse("forum:thread", args=[pk]) + "?page=last")

def new_thread(request, pk):
    """Start a new thread."""
    p = request.POST
    if p["subject"] and p["body"]:
        forum = Forum.objects.get(pk=pk)
        thread = Thread.objects.create(forum=forum, title=p["subject"], creator=request.user)
        Post.objects.create(thread=thread, title=p["subject"], body=p["body"], creator=request.user)
        increment_post_counter(request)
    return HttpResponseRedirect(reverse("forum:forum", args=[pk]))

@login_required
def profile(request, pk):
    """Edit user profile."""
    context = RequestContext(request)

    profile = UserProfile.objects.get(user=pk)
    print('profile=', profile)

    img = None

    if request.method == "POST":
        print("request method is post")

        pf = ProfileForm(request.POST, request.FILES, instance=profile)
        if pf.is_valid():
            print("form is valid")
            print ("image name=", profile.avatar.name)
            pf.save()
            # resize and save image under same filename
            im_path = pjoin(settings.MEDIA_ROOT, profile.avatar.name)
            #im_url = profile.avatar.url

            print('url=', im_path)
            im = PImage.open(im_path)
            im.thumbnail((160,160), PImage.ANTIALIAS)
            #im.save(im_path, "JPEG")
            im.save(im_path, "JPEG")
        else:
            print ("Errors: ", pf.errors)
    else:
        pf = ProfileForm(instance=profile)


    if profile.avatar:
        print ('profile.avatar=', smart_str(profile.avatar), smart_str(profile.avatar.url))
        #img = "/media/" + profile.avatar.name
        img = profile.avatar.url

    context_dict = {'pf': pf, 'img': img, 'profile': profile}
    return render_to_response("forum/profile.html", context_dict, context)

def increment_post_counter(request):
    """We also have to make sure we increment the posts counter
     every time a user replies or creates a thread:"""
    profile = request.user.userprofile_set.all()[0]
    profile.posts += 1
    profile.save()
