import json
import datetime
import csv
import time
from facepy import GraphAPI
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read().decode('utf-8')


# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def getFacebookPageFeedUrl(base_url):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = "&fields=message,link,created_time,type,name,id," + \
        "comments.limit(0).summary(true),shares,reactions" + \
        ".limit(0).summary(true)"

    return base_url + fields


def getReactionsForStatuses(base_url):

    reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
    reactions_dict = {}   # dict of {status_id: tuple<6>}

    for reaction_type in reaction_types:
        fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            reaction_type.upper())

        url = base_url + fields

        data = json.loads(request_until_succeed(url))['data']

        data_processed = set()  # set() removes rare duplicates in statuses
        for status in data:
            id = status['id']
            count = status['reactions']['summary']['total_count']
            data_processed.add((id, count))

        for id, count in data_processed:
            if id in reactions_dict:
                reactions_dict[id] = reactions_dict[id] + (count,)
            else:
                reactions_dict[id] = (count,)

    return reactions_dict


def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_type = status['type']

    status_message = '' if 'message' not in status else \
        unicode_decode(status['message'])
    link_name = '' if 'name' not in status else \
        unicode_decode(status['name'])
    status_link = '' if 'link' not in status else \
        unicode_decode(status['link'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
        datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
        status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
        status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    return (status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares)


def scrapeFacebookPageFeedStatus(page_id1, access_token, since_date, until_date):
    total = 0 
    count = 0
    graph = GraphAPI('EAACEdEose0cBAPtLJurRzWQuf3L0jzczs4OAXnaseF8MKMnAAJKW3zAH1HaepKj7FeC28WdN7v6CNyzLDfj2GhhlxGnpZB3TZA3O2TE89RsPTDTCcVYxZBFrx1ZBE3NnqQuFFwXPHMnZAEG6khLIZCRk50STZB52ULOZBoQLVhwYyyJ3sZCrejdcFGDY3Y0DP5iDfOPqqlZCuXsAZDZD')
    events = graph.search(page_id1, 'page', page=True)

    for col in events:
        for rec in col['data']:
            page_id =rec['id']
            
    #print(page_id)

    with open('{}_facebook_statuses.csv'.format(page_id1), 'w') as file:

        has_next_page = True
        num_processed = 0
        scrape_starttime = datetime.datetime.now()
        after = ''
        base = "https://graph.facebook.com/v2.9"
        node = "/{}/posts".format(page_id)
        node2 = "/{}".format(page_id)
        parameters = "/?limit={}&access_token={}".format(100, access_token)
        since = "&since={}".format(since_date) if since_date \
            is not '' else ''
        until = "&until={}".format(until_date) if until_date \
            is not '' else ''

        #print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))


        base_url1 = base + node2 + parameters + "&fields=name,fan_count"
        total_like = json.loads(request_until_succeed(base_url1))

        #print(int(total_like["fan_count"]))
        total = int(total_like["fan_count"])

        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = base + node + parameters + after + since + until

            url = getFacebookPageFeedUrl(base_url)
            statuses = json.loads(request_until_succeed(url))
            reactions = getReactionsForStatuses(base_url)


            for status in statuses['data']:

                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    status_data = processFacebookPageFeedStatus(status)
                    reactions_data = reactions[status_data[0]]
                    #print(str(status_data[6]))
                    
                    count = count + int(status_data[6])
                    # calculate thankful/pride through algebra
                    num_special = status_data[6] - sum(reactions_data)
                    #w.writerow(status_data + reactions_data + (num_special,))

                num_processed += 1
                    

            # if there is no next page, we're done.
            if 'paging' in statuses:
                after = statuses['paging']['cursors']['after']
            else:
                has_next_page = False

        print("\nDone!\n{} Statuses Processed in {}".format(
              num_processed, datetime.datetime.now() - scrape_starttime))
      
        return count, total







if __name__ == '__main__':

    app_id = "1616760418361922"
    app_secret = "f8a5f48c97a9fffe60933f686d2dc63a"  # DO NOT SHARE WITH ANYONE!

    # input date formatted as YYYY-MM-DD
    since_date = "2017-02-22"
    until_date = "2018-02-22"
    
    access_token = app_id + "|" + app_secret
    
    

    with open('Sample Data.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            motocompany =str((row[0]))
            print(motocompany)
            count, total =scrapeFacebookPageFeedStatus(motocompany, access_token, since_date, until_date)
            print(count)
            print(total)


    # number of  counting / user numbers
    #'Coleman Powersports- Falls Church'


