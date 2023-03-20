from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def parse_xml(xml_data, publisher):
  # Initializing soup variable
    soup = BeautifulSoup(xml_data, 'xml')

  # Creating column for table
    df = pd.DataFrame(columns=['guid', 'title', 'publisher', 'pubDate'])

  # Iterating through item tag and extracting elements
    all_items = soup.find_all('item')
    items_length = len(all_items)
    
    for index, item in enumerate(all_items):
        guid = item.find('guid').text
        title = item.find('title').text
        publisher = publisher
        pub_date = item.find('pubDate').text
        #pub_date = parser.parse(pub_date)
        pub_date = pub_date.replace("GMT", "+0000")
        pub_date = pub_date.replace("EDT", "-0400")
        #pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        #pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            #Sat, 18 Mar 2023 14:33:17 GMT
        
        # Adding extracted elements to rows in table
        row = {
            'guid': guid,
            'title': title,
            'publisher': publisher,
            'pubDate': pub_date,
        }

        df = df.append(row, ignore_index=True)
        #print(f'Appending row %s of %s' % (index+1, items_length))

    return df



urls = []
publishers = []
#urls.append("https://rss.nytimes.com/services/xml/rss/nyt/US.xml")
#publishers.append("New York Times")
urls.append("https://abcnews.go.com/abcnews/topstories")
publishers.append("ABCNews")
urls.append("https://moxie.foxnews.com/google-publisher/latest.xml")
publishers.append("Fox News")
urls.append("https://timcast.com/feed/")
publishers.append("TIMCAST")
#urls.append("https://www.dailymail.co.uk/news/index.rss")
#publishers.append("Daily Mail")
urls.append("https://feeds.feedburner.com/breitbart")
publishers.append("Breitbart News")

#have to prime dfAll by starting with a full df before moving into the loop
urlDZone = "https://feeds.dzone.com/home"
publisherDZone = "Developer Zone"
xml_data = requests.get(urlDZone).content 
dfAll = parse_xml(xml_data, publisherDZone)

for index in range(len(urls)):
    dfTemp = dfAll
    xml_data = requests.get(urls[index]).content 
    dfTemp2 = parse_xml(xml_data, publishers[index])
    dfAll = pd.concat([dfTemp, dfTemp2], ignore_index=True)


dfAll.sort_values(by=['pubDate'], inplace=True, ascending=False)
#dfAll.to_csv('news.csv')

"""
df = pd.read_csv(
    "https://data.boston.gov/dataset/c8b8ef8c-dd31-4e4e-bf19-af7e4e0d7f36/resource/29e74884-a777-4242-9fcc-c30aaaf3fb10/download/economic-indicators.csv",
    parse_dates=[["Year", "Month"]],
)
length = len(df)
"""

df = dfAll
length = len(df)



app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN8888"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/runscript")
def ScriptPage():
    # Type what you want to do when the user clicks on the link.
    #
    # Once it is done with doing that code... it will
    # redirect back to the homepage
    return redirect(url_for("index"))

@app.route("/df")
def dataframe():
    return render_template("df.html", length=length, dataframe=df.to_html())


@app.route("/dfcustom")
def dfcustom():
    data = df.to_dict(orient="records")
    headers = df.columns
    print(headers)
    return render_template("dfcustom.html", data=data, headers=headers)


if __name__ == "__main__":
    app.run(debug=True, port=5957)