from flask import Flask, render_template, jsonify, request
import requests
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
from flask_cors import CORS,cross_origin
import pymongo
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello():
    return render_template("html_custom.html")


@app.route("/service", methods=['GET','POST'])
def search():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")
        try:
            #url_mongo = f"mongodb://localhost:27017/"
            url_mongo = "mongodb+srv://oury:touga@oury.p7kgd.mongodb.net/reviews_new?retryWrites=true&w=majority"
            clien = pymongo.MongoClient(os.getenv(url_mongo), ssl= True, ssl_cert_reqs='CERT_NONE')
            dataBase = clien["reviews_new"]
            review = dataBase[searchString]
            xl = review.find({})
            if xl.count() > 0:
                return render_template("results_mine.html", result=xl)
            else:
                flipkart_url = "https://www.flipkart.com/search?q="+searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                productlink = "https://flipkart.com"+box.div.div.div.a["href"]
                page = requests.get(productlink)
                beauty_page = bs(page.text, "html.parser")  # parsing the product page as HTML
                comment_section = beauty_page.find_all("div", {"class": "_16PBlm"})
                reviews = []
                table = dataBase[searchString]
                for rating_heading_comment_name in comment_section:

                    try:
                        rating = rating_heading_comment_name.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text
                    except:
                        rating = "No rating"

                    try:
                        heading = rating_heading_comment_name.findAll("p", {"class": "_2-N8zT"})[0].text
                    except:
                        heading = "No heading"

                    try:
                        comment = rating_heading_comment_name.findAll("div", {"class": ""})[0].div.text
                    except:
                        comment = "No comment"

                    try:
                        name = rating_heading_comment_name.findAll("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
                    except:
                        name = "No name"

                    reviews_summary = {"product": searchString,"rating": rating,"heading": heading,"comment": comment,"name": name}
                    x=table.insert_one(reviews_summary)
                    reviews.append(reviews_summary)
                return render_template("results_mine.html", result=reviews)
        except:
            return "something is wrong"
    else:
        render_template("html_custom.html")
if __name__ == "__main__":
    app.run(debug=True)
