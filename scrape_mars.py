from bs4 import BeautifulSoup as bs
from splinter import Browser
import time
import pandas as pd
import requests
import datetime

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    #NASA Mars news
    nasa_url = 'https://mars.nasa.gov/news/'

    browser = init_browser()
    browser.visit(nasa_url)
    time.sleep(1)

    nasa_soup = bs(browser.html,'html.parser')

    browser.quit()

    stories = nasa_soup.body.find('ul', class_='item_list')
    first_story = stories.find('li', class_='slide')

    story_title = f"News: {first_story.find('div', class_='content_title').text}"
    story_text = first_story.find('div', class_='article_teaser_body').text


    #JPL Mars space images
    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    
    browser = init_browser()
    browser.visit(jpl_url)

    jpl_soup = bs(browser.html, 'html.parser')

    browser.quit()

    featured_image = jpl_soup.find('article', class_='carousel_item')
    featured_image_style = featured_image['style']

    featured_image_url = str.replace(featured_image_style,"background-image: url('",'')
    featured_image_url = str.replace(featured_image_url,"');",'')

    featured_image_url = str.replace(jpl_url,'/spaceimages/?search=&category=Mars',featured_image_url)
    featured_image_alt = featured_image['alt']


    #Mars weather
    weather_url = 'https://twitter.com/marswxreport?lang=en'

    browser = init_browser()
    browser.visit(weather_url)
    
    weather_soup = bs(browser.html,'html.parser')

    browser.quit()

    timeline = weather_soup.body.find('div', class_='ProfileTimeline')
    latest_tweet = timeline.find('li', class_='js-stream-item')

    mars_weather = latest_tweet.find('p', class_='tweet-text').text

  
    #Mars facts
    facts_url = 'https://space-facts.com/mars/'

    mars_table = pd.read_html(facts_url)[0]

    mars_facts = pd.DataFrame.to_html(mars_table, index=False, header=False)


    #Mars hemispheres
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser = init_browser()
    browser.visit(hemispheres_url)

    hemispheres_soup = bs(browser.html,'html.parser')

    browser.quit()

    results = hemispheres_soup.body.find('div', class_='result-list')
    hemisphere_results = results.find_all('div', class_='item')

    hemisphere_image_urls = []

    for hemisphere in hemisphere_results:
        hemisphere_description = hemisphere.find('div',class_='description')
        
        hemisphere_name = hemisphere_description.find('h3').text
        hemisphere_name = str.replace(hemisphere_name,' Enhanced', '')
        
        hemisphere_link = hemisphere.find('a', class_='itemLink')['href']
        hemisphere_link = str.replace(hemispheres_url,'/search/results?q=hemisphere+enhanced&k1=target&v1=Mars',hemisphere_link)
        
        image_html = requests.get(hemisphere_link).text
        image_soup = bs(image_html,'html.parser')
        
        image = image_soup.find('div', class_='wide-image-wrapper').find('img', class_='wide-image')
        
        image_url = image['src']
        image_url = str.replace(hemispheres_url,'/search/results?q=hemisphere+enhanced&k1=target&v1=Mars', image_url)
        
        hemisphere_dict = {'title': hemisphere_name,
                        'image_url': image_url}
        
        hemisphere_image_urls.append(hemisphere_dict)
    

    #Scrape date/time
    curr_date_time = datetime.datetime.now()
    hour = int(datetime.datetime.strftime(curr_date_time,'%H'))

    if hour >=12:
        am_pm = 'PM'
        curr_date_time = curr_date_time - datetime.timedelta(hours=12)
    else:
        am_pm = "AM"
    
    scrape_date = f"{datetime.datetime.strftime(curr_date_time,'%m/%d/%Y %H:%M')} {am_pm}"

    mars_data = {
        "story_title": story_title,
        "story_text": story_text,
        "featured_image_url": featured_image_url,
        "featured_image_alt": featured_image_alt,
        "weather": mars_weather,
        "facts": mars_facts,
        "hemisphere_image_urls": hemisphere_image_urls,
        "scrape_date": scrape_date
    }

    return mars_data