from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import datetime as dt


def scrape_all():

    # Initiate headless driver for deployment
    executable_path = {'executable_path':'c:/Users/Haile/Downloads/chromedriver_win32/chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "weather": weather_tweet(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get first list item and wait one second if not immediately present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        news_soup1 = news_soup.select_one("ul.item_list li.slide")
        news_title = news_soup1.find("div", class_="content_title").get_text()
        news_paragraph = news_soup1.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_paragraph


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # Find and click the full image button
    full_image = browser.find_by_id("full_image")
    full_image.click()

    #Use beautiful soup to convert the browser html to a soup object 
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_elem = browser.find_link_by_partial_text("more info")
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_bs = BeautifulSoup(html, "html.parser")

    # image url
    img = img_bs.select_one("figure.lede a img")

    try:
        img_url = img.get("src")

    except AttributeError:
        return None

    # Use the base url to create a featured image url
    featured_image_url = f"https://www.jpl.nasa.gov{img_url}"

    return featured_image_url


def weather_tweet(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_bs = BeautifulSoup(html, "html.parser")

    # Find a tweet with the data-name `Mars Weather`
    tweet_attr = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_bs.find("div", attrs=tweet_attr)

    #Identify within the tweet for the p tag containing the text and 
     #output it mars_weather
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["Parameter", "Value"]
    df.set_index("Parameter", inplace=True)

    
    return df.to_html(classes="table table-striped")

def hemispheres(browser):

    
    url ="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


    browser.visit(url)

    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_img = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_img)

        # navigate backwards
        browser.back()

    return hemisphere_image_urls


def scrape_hemisphere(html_text):

    # # Use beautiful soup to convert the browser html to a soup object
    hemi_bs = BeautifulSoup(html_text, "html.parser")

    # geting href and text 
    try:
        title_text = hemi_bs.find("h2", class_="title").get_text()
        sample_img = hemi_bs.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None 
        title_text = None
        sample_img = None

    hemisphere = {
        "title": title_text,
        "img_url": sample_img
    }

    return hemisphere




if __name__ == "__main__":

    # print scraped data
    print(scrape_all())