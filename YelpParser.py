"""
This program requires an input of a list of businesses that have been scraped 
from GooglePlaces. It then proceeds to visit the Yelp page of the company
corresponding to its phone number, and then stores additional data to the passed in
list, such as the company's Yelp rating, and number of reviews.
"""

from yelpapi import YelpAPI
import json
import re
import time

APIKEY = "BDF_tYMOnEwm0jPojGG5Jb3Syj4FyGA7KPxu-L4ze8aLsUXtH_Hag1ezCEQc65wqDHiQjLcIfG3wbiu_xPZk9aIrYQuxKvTPUIRkUxeC5bK6lK73doWNGJzIn-OOWnYx"

def strip(str1):
    """
    brief: Remove all comma from a string for it to be later stored in csv file
    param str1: given string
    return the given string with all comma stripped off
    """
    str1 = str1.replace(',', '')
    return str1

def changeFormatTel(tel):
  """
  This function takes in string that represents the international telephone number 
  of a business, and convert it to a string of numbers without any space or
  non-numeric characters.
  param: tel given string that represents the international telephone number 
         of a business
  return: the reformated telephone number without any space or
         non-numeric characters.
  """
  updatedNum = re.sub('[^0-9]', '', tel)
  updatedNum.replace(" ","")
  return updatedNum


def parseYelpData(places, heading = "tel"):
  """
  This function takes in a list of businesses and looks them up by phone number
  in Yelp Fusion using yelpapi. It adds data about Yelp average rating of the
  business, the number of Yelp reviews, and the company's Yelp link to the 
  dictionary of the business. The function then returns the updated list of businesses.
  param: places list of businesses that have been scraped by the GoogleParser
  param: heading default to "tel", signifying the heading for the phone number data
         field of each business
  return: updated list of businesses, with these data fields added to each business:
          'yelp_rating', 'yelp_review_count', 'yelp_url'
  """

  yelp_api = YelpAPI(APIKEY)

  for place in places:
    phoneNum = changeFormatTel(place[heading])
    if phoneNum == "":
      place['yelp_rating'] = ""
      place['yelp_review_count'] = ""
      place['yelp_url'] = ""
      continue

    response = yelp_api.phone_search_query(phone=str(phoneNum))


    # If the phone number is listed in Yelp, add Yelp rating, review_count, and
    # yelpUrl to the dictionary of the business.
    if response['total'] != 0:
      business = response['businesses'][0]
      place['yelp_rating'] = strip(str(business['rating']))
      place['yelp_review_count'] = strip(str(business['review_count']))
      place['yelp_url'] = strip(str(business['url']))
    else:
      place['yelp_rating'] = ""
      place['yelp_review_count'] = ""
      place['yelp_url'] = ""

    # to avoid Yelp's error messages of too many queries per second
    time.sleep(1)
  return places
