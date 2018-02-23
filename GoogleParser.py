"""
This program uses the library python-google-places and scrapes data about
businesses that match with the given query, and within a given radius of
a given location. It stores data about businesses in a list. 
"""
from googleplaces import GooglePlaces, types, lang 
import pprint

API_KEY = 'AIzaSyCtgmj9wswe42uYL3KAQzpG3sB94RCvL-U'
google_places = GooglePlaces(API_KEY)

def strip(str1):
    """
    brief: Remove all comma from a string for it to be later stored in csv file
    param str1: given string
    return the given string with all comma stripped off
    """
    str1 = str1.replace(',', '')
    return str1

def parseGoogleData(_query='motorbikes in Virginia',_location='Virginia',_radius=40000):
    """
    brief: This function scraps Google data for businesses that match with the 
           given query, and within _radius meter of the _location. It then stores
           the attribute and corresponding value of each place into a dictionary,
           and return a list of such places.
    param _query: query string for search results to be compared against
    param _location: a human-readable location location to search for the query
    param _radius: expand the search within this radius of the location, in meters
    return: a non-repeated list of business that match with the given query, and
            within _radius meter of the _location, each business represented as 
            a dictionary. The keys in each dictionary are 'name', 'address', 'lat',
            'lng','tel','website','google_url','google_rating','google_reviews_count',
            'opening_hours'
            Any key for which GooglePlace API cannot find information on, value is
            default to empty string.
    """
    query_result = google_places.text_search(query=_query, location=_location, 
        radius=_radius)

    places = list()
    phoneNumbers = list()

    # counter to move through at most 6 pages of results or when all results are exhausted
    j = 0
    while True:
        # Loop through places in the first query result
        for place in query_result.places:

            # Get necessary details about places before accessing data
            # Referencing the attributes below, prior to making a call to
            # get_details() will raise a googleplaces.GooglePlacesAttributeError.
            place.get_details()
        
            # Prevent duplicates by comparing phone numbers
            if(place.international_phone_number in phoneNumbers):
                continue
            phoneNumbers.append(place.international_phone_number)

            placeDict = dict()

            # Store information about place to dictionary
            # If a particular attribute is not available, store empty string
            
            placeDict['name'] = strip(place.name)              # name of business
            if(place.vicinity is not None):
                placeDict['address'] = strip(place.vicinity)   # address of business
            else:
                placeDict['address'] = ""
            if(place.geo_location is not None):
                placeDict['lat'] = strip(str(place.geo_location['lat']))    # latitude
                placeDict['lng'] = strip(str(place.geo_location['lng']))    # longtitude
            else:
                placeDict['lat'] = ""
                placeDict['lng'] = ""
            if(place.international_phone_number is not None):  # international phone number
                placeDict['tel'] = strip(str(place.international_phone_number))    
            else:
                placeDict['tel'] = ""
            if(place.website is not None):                     # website of the business
                placeDict['website'] = strip(str(place.website))
            else:
                placeDict['website'] = ""
            if(place.url is not None):                         # url of the google place review
                placeDict['google_url'] = strip(str(place.url))
            else:
                placeDict['google_url'] = ""
            if(place.rating is not None):                      # rating of the business
                placeDict['google_rating'] = strip(str(place.rating))
            else:
                placeDict['google_rating'] = "" 

            # Retrieve information about opening hours and number of reviews
            if place.details.get('reviews') is not None:
                placeDict['google_reviews_count'] = str(len(place.details.get('reviews')))
            else:
                placeDict['google_reviews_count'] = "0"

            openingHourInfo = ""
            if(place.details.get('opening_hours') is not None):
                openingHours = place.details.get('opening_hours').get('weekday_text')
                for day in openingHours:
                    openingHourInfo += day
                    openingHourInfo += "/ "
            placeDict['opening_hours'] = openingHourInfo

            # Add new entry point to list places       
            places.append(placeDict)

        j += 1
        if j > 30:
            break
        # if query_result has next page, continue browsing through the next pages
        if(query_result.has_next_page_token):
            query_result = google_places.text_search(
                pagetoken=query_result.next_page_token)
        else:
            break

    return places


