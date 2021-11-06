# Import dependencies 
from splinter import Browser
from bs4 import BeautifulSoup as soup
#from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():

    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    #Step 1: Create data dictionary to hold a list of dictionaries of url and title
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image_info": hemisphere_image(browser)
    }

    browser.quit()
    return data

def mars_news(browser):
    
    # Scrape Mars News
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert browser html to soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p

# Featured Images
def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('img', class_='fancybox-image').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
        
    return img_url

# Mars Facts
def mars_facts():

    # Add try/except for error handling
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com/')[0]
    
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


#Step 2: Create a function that will scrape the hemisphere data
def hemisphere_image(browser):
    
    # Visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    # Create list to hold the images and titles.
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere
    # Parse with soup
    html = browser.html
    main_page_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # number of pics to scan
        pics_count = len(main_page_soup.select("div.item"))

        # loop over each sample pic
        for i in range(pics_count):
            
            results = {}

            #Find link and open
            link_image = main_page_soup.select("div.description a")[i].get('href')
            browser.visit(f'https://marshemispheres.com/{link_image}')
        
            # Parse the new html
            html = browser.html
            sample_image_soup = soup(html, 'html.parser')
            
            # Get the link and title
            url_image = sample_image_soup.select_one("div.downloads ul li a").get('href')
            url_image = f'https://marshemispheres.com/{url_image}'
            img_title = sample_image_soup.select_one('h2.title').get_text()
            
            results = {
                'url_image': url_image,
                'img_title': img_title}
        
            hemisphere_image_urls.append(results)
        
            # Return to main page
            browser.back()

    except BaseException:
        return None
    
    # Return list
    #print(hemisphere_image_urls)  
    return hemisphere_image_urls 


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())