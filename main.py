"""A module that generates a web page with a map
on which images of the nearest filming locations
of a given year.

Input: year, coords (example: 24.1234, 24.1234)
Output: webpage
"""


import folium
import mpu
from geopy.geocoders import Nominatim


def input_data(file_name: str):
    """The function reads data from the file with
    the name specified in the parameter and returns
    them in the form of a list.

    str -> list
    """
    read = False
    data = []
    file = open(file_name)
    while 1:
        line = file.readline()
        if line.startswith("---") and read:
            break
        if read:
            split_line = line.split("\t")
            if line.startswith('"'):
                data.append({"title": split_line[0].split('" ')[0][1:],
                             "year": split_line[0].split('" ')[1].split(")")[0][1:],
                             "location": split_line[-1][:-1]})
            else:
                data.append({"title": split_line[0].split(" (")[0],
                             "year": split_line[0].split(" (")[1].split(")")[0],
                             "location": split_line[-1][:-1]})
        if line.startswith("==="):
            read = True
    return data


def films_by_year(data, year):
    """The function from the list of films selects
    only films of the corresponding year specified
    in the parameter.

    (list, str) -> list

    >>> films_by_year([{'title': 'Ьз Maymun', 'year': '2008', 'location': 'Istanbul, Turkey'}, \
    {'title': 'Ьз kagitзilar', 'year': '1976', 'location': 'Turkey'}], '2008')
    [{'title': 'Ьз Maymun', 'year': '2008', 'location': 'Istanbul, Turkey'}]
    """
    return [film for film in data if film['year'] == year]


def films_locations(data):
    """The function searches for coordinates
    (longitude and latitude) of movies in the list.

    list -> list

    >>> films_locations([{'title': 'Ьз Maymun', 'year': '2008', 'location': 'Istanbul, Turkey'}])
    [{'title': 'Ьз Maymun', 'year': '2008', 'location': 'Istanbul, Turkey', 'coords': (41.0096334, 28.9651646)}]
    """
    films = []
    geolocator = Nominatim(user_agent="app")
    for film in data:
        try:
            location = geolocator.geocode(film["location"])
            film["coords"] = (location.latitude, location.longitude)
            films.append(film)
        except AttributeError:
            film["coords"] = None
    return films


def nearby_locations(films, position, number):
    """The function sorts the list of films by
    distance to a given point, and returns a
    certain number of the closest ones.

    (list, list, int) -> list
    """
    for film in films:
        film["distance"] = mpu.haversine_distance(position, film['coords'])
    films.sort(key=lambda x: x["distance"])
    return films[0:number]


# Input year and position
# 49.83826, 24.02324
generate_year = input("Please enter a year you would like to have a map for: ")
line_position = input("Please enter your location (format: lat, long): ")
generate_position = [float(coord) for coord in line_position.split(",")]

earth_map = folium.Map(location=generate_position, zoom_start=5)

print("Map is generating...")
markers = nearby_locations(films_locations(films_by_year(input_data("locations.list"), generate_year)),
                           generate_position, 10)

print("Please wait...")
fg = folium.FeatureGroup(name="Nearest location where movies were filmed.")
for marker in markers:
    fg.add_child(folium.Marker(location=marker["coords"],
                 popup="Title: " + marker["title"] + ", year: " + marker["year"] +
                 ", location: " + marker["location"], icon=folium.Icon()))
earth_map.add_child(fg)

earth_map.save(generate_year + "_movie_map.html")
print("Finished. Please have look at the map " + generate_year + "_movies_map.html")
