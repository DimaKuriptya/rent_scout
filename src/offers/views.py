from django.shortcuts import render
from .utils import get_data


def view_offers(request):
    return render(request, 'offers/view_offers.html', {'data': get_data()})
