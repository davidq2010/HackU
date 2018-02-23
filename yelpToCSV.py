"""
This program requires an input of either CSV file of phone numbers or list of
phone numbers. It then proceeds to visit the Yelp page of the company
corresponding to that phone number, and then returns a CSV of the company
rating, number of reviews, and top 3 reviews chosen by Yelp.

If main, require CSV. Else, require list.
If Yelp JSON has a 'total' value of 0, just continue to next phone number.
"""

import pandas as pd
from yelpapi import YelpAPI
import argparse
import json
from pprint import pprint
import re

APIKEY = "BDF_tYMOnEwm0jPojGG5Jb3Syj4FyGA7KPxu-L4ze8aLsUXtH_Hag1ezCEQc65wqDHiQjLcIfG3wbiu_xPZk9aIrYQuxKvTPUIRkUxeC5bK6lK73doWNGJzIn-OOWnYx"


def getPhoneFromCSV(fileName, tel):
  """
  This function takes in a CSV from Google Places data and isolates the phone
  number column into a list, which it returns.

  param: fileName = String of file name
  param: tel = String of header of column of phone numbers
  return: data = List of phone numbers obtained from fileName
  """
  df = pd.read_csv(fileName)

  # Look up column with 'tel' heading
  saved_column = list(df[tel])
  data = list()

  for phone in saved_column:
    # Output phone numbers of just numbers
    updatedNum = re.sub('[^0-9]', '', str(phone))
    updatedNum.replace(" ","")
    data.append(updatedNum)

  # Return data list of phone numbers without empty elements
  return filter(None, data)


def getYelpData(phoneNums):
  """
  This function takes in a list of phone numbers and looks them up in Yelp
  Fusion using yelpapi. It then returns 2 dictionaries of the business'
  information and three pertinent user reviews of the business.

  param: phoneNums = List of phone numbers
  return: phoneDict = Dictionary mapping a phone number to a list.
                      list[0] = the business' rating
                      list[1] = the business' review count
                      list[2] = the business' url
  return: reviewDict = Dictionary mapping a phone number to a list of reviews
  (up to 3 reviews available, chosen by Yelp algorithm)
                      list[0] = the review's rating
                      list[1] = the review's text
                      list[2] = the review's time of creation (IN PACIFIC TIME)
  """

  yelp_api = YelpAPI(APIKEY)

  phoneDict = dict()
  reviewDict = dict()
  #lineNum = 1

  for phoneNum in phoneNums:
    #print(lineNum)
    response = yelp_api.phone_search_query(phone=str(phoneNum))
    #print(phoneNum)
    #pprint(response)

    #lineNum = lineNum + 1

    # If the phone number is listed in Yelp, store rating, review_count, url in
    # array mapped to phone number. Then, use the business-id field from
    # response to store 3 reviews in a separate list. Return both at end.
    if response['total'] != 0:
      business = response['businesses'][0]
      phoneDict[phoneNum] = [business['rating'], business['review_count'],
      business['url']]

      # Get reviews using company id and store in reviewDict
      companyID = str(business['id'])
      reviewResponse = yelp_api.reviews_query(id=companyID)
      reviewList = reviewResponse['reviews']

      # Put a list of review information in reviewDict (mapped to phone number)
      for review in reviewList:
        reviewDict[phoneNum] = [review['rating'], review['text'],
        review['time_created']]

  return phoneDict, reviewDict


if __name__ == "__main__":
  """
  Optional command of header name for phone numbers in Google Places file
  """
  # Use command line arg to load a file
  argparser = argparse.ArgumentParser()
  argparser.add_argument('csv_file', type=str, help='Name of csv file')
  argparser.add_argument('--tel', type=str, help='Header of phone # column')
  args = argparser.parse_args()
  fileName = args.csv_file
  if args.tel != None:
    telName = args.tel
  else:
    telName = 'tel'
  data = getPhoneFromCSV(fileName, telName)
  phoneDict, reviewDict = getYelpData(data)
  #pprint(phoneDict)
  #print('\n')
  #pprint(reviewDict)
