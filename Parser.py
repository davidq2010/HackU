from YelpParser import parseYelpData
from GoogleParser import parseGoogleData
import argparse

if __name__ == "__main__":
  
  # Use command line arg to load a file
  argparser = argparse.ArgumentParser()
  argparser.add_argument('csv_file', type=str, help='Name of csv file')
  args = argparser.parse_args()
  fileName = args.csv_file
  fh = open(fileName, "a")

  # retrieve information of businesses based on GooglePlaces data, then add
  # Yelp data
  businesses = parseGoogleData('automotive in Virginia','Virginia', 49000)
  businesses = parseYelpData(businesses)
  fh.write('name,address,lat,lng,tel,website,google_url,google_rating,' +
    'google_reviews_count,opening_hours,yelp_rating,yelp_review_count,' +
    'yelp_url,is_listed_yelp,is_claimed_yelp,empty_col\n')
  for business in businesses:
    for k, v in business.items():
      fh.write(v + ',')
    fh.write("")
    fh.write('\n')

  fh.close()

