from django.shortcuts import render, redirect
from .forms import EventRegistrationForm

def register_event_view(request):
    if request.method == "POST":
        # form with POST data
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form data if valid
            form.save()
            return redirect('thank_you')  # Redirect to thank-you page
    else:
        #  empty form for GET request
        form = EventRegistrationForm()

    return render(request, 'register_event.html', {'form': form})

def thank_you_view(request):
    return render(request, 'thank_you.html')
