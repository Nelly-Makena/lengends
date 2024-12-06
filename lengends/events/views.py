from django.shortcuts import render, redirect
from .forms import EventRegistrationForm

# Handle form submission
def register_event_view(request):
    if request.method == "POST":
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form data
            form.save()
            return redirect('thank_you')  # redirect to thank u page
    else:
        form = EventRegistrationForm()

    return render(request, 'register_event.html', {'form': form})

# Render the thank-you page
def thank_you_view(request):
    return render(request, 'thank_you.html')
