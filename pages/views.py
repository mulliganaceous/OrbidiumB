import json
from django.shortcuts import render
from django.http import JsonResponse
from pages.models import MinorPlanetBody
from pages.tests import MAINBELT_ONES
import urllib.request

# Create your views here.

def asteroids(request):
    if request.method == 'GET':
        return render(request, "pages/asteroids.html", {})

    if request.method == 'POST':
        return render(request, "pages/asteroids.html", {})

def load_ephemeris(asteroid_label):
    url = "https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=%s&cd-tp=true" % asteroid_label
    data = urllib.request.urlopen(url).read()
    return data

def api(request):
    # load from DB
    asteroid_list = []
    subset = request.GET.get('subset', None)
    mpc_id = request.GET.get('mpc_id', None)
    resultset = None
    if subset == 'mba':
        return JsonResponse({"pha":[],"mba":MAINBELT_ONES}, safe=False)
    if subset == 'pha':
        resultset = MinorPlanetBody.objects.filter(attributes__contains='>1km PHA')
    if subset == 'nea':
        resultset = MinorPlanetBody.objects.filter(attributes__contains='NEO')
    if subset == 'trj':
        resultset = MinorPlanetBody.objects.filter(attributes__contains='Trojan')
    if subset == 'kbo':
        resultset = MinorPlanetBody.objects.filter(radius_p__gte=30.33, radius_a__lte=55.0)
    if subset == 'sdo':
        resultset = MinorPlanetBody.objects.filter(radius_p__gte=30.33, radius_a__gte=55.0)
    if subset == 'dto':
        resultset = MinorPlanetBody.objects.filter(radius_p__gte=55.00)
    if subset == 'cnt':
        resultset = MinorPlanetBody.objects.filter(radius_p__gte=5.45, radius_a__lte=30.0)
    if subset == 'all':
        resultset = MinorPlanetBody.objects.all()
    if subset == 'one':
        resultset = MinorPlanetBody.objects.filter(asteroid_name__contains=mpc_id)

    for x in resultset:
        obj_data = {}
        obj_data["id"] = x.asteroid_id
        obj_data["name"] = x.asteroid_name
        obj_data["flags"] = x.flags_short
        obj_data["attrs"] = x.attributes
        obj_data["mag"] = x.magnitude
        obj_data["semimajor_a"] = x.semimajor_a
        obj_data["radius_a"] = x.radius_a
        obj_data["radius_p"]= x.radius_p
        obj_data["eccentricity"] = x.eccentricty
        obj_data["inclination"] = x.inclination
        obj_data["mean_anomaly"] = x.mean_anomaly
        obj_data["argument_perihelion"] = x.argument_perihelion
        obj_data["asc_node_longitude"] = x.asc_node_longitude
        obj_data["mean_daily_motion"] = x.mean_daily_motion
        if subset =='one':
            ephemeris = json.loads(load_ephemeris(mpc_id))
            for element in ephemeris["orbit"]["elements"]:
                if element["name"]=='tp_cd':
                    obj_data['tpa'] = element["value"]
        else:
            obj_data['tpa'] = None
        asteroid_list.append(obj_data)
    return JsonResponse({"pha":asteroid_list,"mba":[]}, safe=False)