from django.shortcuts import redirect, render

def logout(request):
    try:
        del request.session['user']
    except:
        return redirect('login')
    return redirect('login')