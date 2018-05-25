from django.shortcuts import render

def main(request):
    return render(request,'main.html')
def piano_note(request):
    return render(request,'note.html')
