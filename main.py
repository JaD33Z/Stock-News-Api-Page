from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
Bootstrap(app)

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_KEY")
STOCK_API_KEY = os.environ.get("STOCK_KEY")


class StockChoice(FlaskForm):
    stock_name = StringField("Name of Stock", validators=[DataRequired()])
    company_name = StringField("Name of Company", validators=[DataRequired()])
    submit = SubmitField("Check recent Activity")


@app.route('/', methods=["GET", "POST"])
def home():
    form = StockChoice()
    if form.validate_on_submit():
        STOCK_NAME = request.form['stock_name']
        COMPANY_NAME = request.form['company_name']
        stock_params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": STOCK_NAME,
            "bestMatches": STOCK_NAME,
            "apikey": STOCK_API_KEY,
        }
        response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
        data_daily = response.json()["Time Series (Daily)"]
        data_list = [value for (key, value) in data_daily.items()]
        yesterday_close = data_list[0]["4. close"]
        day_before_close = data_list[1]["4. close"]
        up_down = None
        pos_diff = (float(yesterday_close) - float(day_before_close))
        if pos_diff > 0:
            up_down = "🔺"
        else:
            up_down = "🔻"
        percentage_diff = round((pos_diff / float(yesterday_close)) * 100)

        if abs(percentage_diff):
            news_params = {
                "q": COMPANY_NAME,
                "apiKey": NEWS_API_KEY,
            }
            news_data = requests.get(url=NEWS_ENDPOINT, params=news_params)
            news_articles = news_data.json()["articles"]

            recent_articles = news_articles[:3]
            if len(recent_articles) < 3:
                flash('No results found.')
                return redirect(url_for('home'))

            first_3_articles = [
                f"{STOCK_NAME} {up_down} %{percentage_diff} \nHeadline: {article['title']}. \nBrief: {article['description']}. \nUrl: {article['url']} "
                for article in recent_articles]

            return render_template('index.html', form=form, articles=first_3_articles)

    return render_template('index.html', form=form)


@app.route('/info')
def page_info():
    return render_template('info.html')




if __name__ == "__main__":
    app.run(debug=True)