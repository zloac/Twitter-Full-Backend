from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from posts.models import *

def begen(request):
    postId = request.POST['postId']
    post = Post.objects.get(id = postId)
    # İşlem yapılabilmesi için girişli olması gerekiyor
    if request.user.is_authenticated:
        # Hangisine bastığını algılamak için
        if 'begen' in request.POST:
            # Aynı kullanıcı daha öncesinde beğenmiş mi 
            if Post.objects.filter(like__in = [request.user], id = postId).exists():
                post.like.remove(request.user)
                post.save()
                
            else:
                post.like.add(request.user)
                post.dislike.remove(request.user)
                post.save()
                
        if 'begenme' in request.POST:
            if Post.objects.filter(dislike__in = [request.user], id = postId).exists():
                post.dislike.remove(request.user)
                post.save()
            else:
                post.dislike.add(request.user)
                post.like.remove(request.user)
                post.save()
        if 'paylas' in request.POST:
            if Post.objects.filter(retweet__in = [request.user], id = postId).exists():
                post.retweet.remove(request.user)
                post.save()
            else:
                post.retweet.add(request.user)
                post.save()
    
# Create your views here.
def userRegister(request):
    if request.method == "POST":
        kullanici = request.POST['kullanici']
        email = request.POST['email']
        isim = request.POST['isim']
        soyisim = request.POST['soyisim']
        sifre1 = request.POST['sifre1']
        sifre2 = request.POST['sifre2']

        if sifre1 == sifre2:
            if User.objects.filter(username = kullanici).exists():
                messages.error(request, 'Kullanıcı adı kullanımda')
                return redirect('register')
            elif User.objects.filter(email = email).exists():
                messages.error(request, 'Bu email kullanımda')
                return redirect('register')
            elif len(sifre1) < 6:
                messages.error(request, 'Şifre en az 6 karakter olmalıdır')
                return redirect('register')
            else:
                user = User.objects.create_user(username = kullanici, email = email, password = sifre1)
                Hesap.objects.create(
                    user = user,
                    isim = isim,
                    soyisim = soyisim, 
                ) 
                user.save()
                messages.success(request, 'Kayıt başarılı')
                return redirect('index')
        else:
            messages.error(request, 'Şifreler uyuşmuyor')    
            return redirect('register')
    return render(request, 'user/register.html')


def userLogin(request):
    if request.method == 'POST':
        kullanici = request.POST['kullanici']
        sifre = request.POST['sifre']

        user = authenticate(request, username = kullanici, password = sifre)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Giriş yapıldı')
            return redirect('index')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı')
            return redirect('login')
    return render(request, 'user/login.html')


def userLogout(request):
    logout(request)
    messages.success(request, 'çıkış yapıldı')
    return redirect('index')


def profil(request):
    user = request.user
    paylasim = Post.objects.filter(owner = request.user)
    begeni = Post.objects.filter(like__in = [request.user])
    retweet = Post.objects.filter(retweet__in = [request.user])

    if request.method == 'POST':
        begen(request)
        return redirect('profil')
    context = {
        'user':user,
        'paylasim':paylasim,
        'begeni':begeni,
        'retweet':retweet
    }
    return render(request, 'user/profil.html', context)

def update(request):
    user = request.user.hesap
    form = HesapForm(instance = user)
    if request.method == 'POST':
        form = HesapForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            # hesap = form.save(commit = False)
            # user.isim = hesap.isim
            form.save()
            messages.success(request, 'Profil güncellendi')
            return redirect('profil')

    context = {
        'form':form
    }
    return render(request, 'user/duzenle.html', context)

def sifre(request):
    user = request.user
    if request.method == 'POST':
        eski = request.POST['eski']
        yeni1 = request.POST['yeni1']
        yeni2 = request.POST['yeni2']

        yeni = authenticate(request, username = user, password = eski)
        
        if yeni is not None:
            if yeni1 == yeni2:
                user.set_password(yeni1)
                user.save()
                messages.success(request, 'Şifre değiştirildi')
                return redirect('login')
            else:
                messages.error(request, 'Şifreler uyuşmuyor')
                return redirect('sifre')
        else:
            messages.error(request, 'Mecvut şifreniz hatalı')
            return redirect('sifre')
    return render(request, 'user/sifre.html')

def userProfil(request, pk):
    user = User.objects.get(id = pk)
    paylasim = Post.objects.filter(owner = user)
    begeni = Post.objects.filter(like__in = [user])
    retweet = Post.objects.filter(retweet__in = [user])
    
    if request.method == 'POST':
        if 'takip' not in request.POST:
            begen(request)
        if 'takip' in request.POST:
            if request.user.is_authenticated:
                hesabim = Hesap.objects.get(user = request.user)
                if Hesap.objects.filter(user = request.user, takip__in = [user]).exists():
                    hesabim.takip.remove(user)
                    user.hesap.takipci.remove(request.user)
                    hesabim.save()
                    
                else:
                    hesabim.takip.add(user)
                    user.hesap.takipci.add(request.user)
                    
                    hesabim.save()
        return redirect('userProfil', pk = user.id)
        
    context = {
        'user':user,
        'paylasim':paylasim,
        'begeni':begeni,
        'retweet':retweet
    }
    return render(request, 'user/user-profil.html', context)