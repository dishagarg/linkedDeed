from __future__ import print_function  # In python 2.
from bs4 import BeautifulSoup, SoupStrainer  # For HTML parsing
import urllib2  # Website connections
import re  # Regular expressions
import unicodedata
from time import sleep  # To prevent overwhelming the server between connections
import pandas as pd  # For converting results to a dataframe and bar chart plots
import sys


def job_extractor(website):
    """Clean up the raw HTML."""
    company_name = "Unknown"
    try:
        site = urllib2.urlopen(website).read()  # Connect to the job posting
    except:
        return   # Need this in case the website isn't there anymore or some other weird connection problem 
    soup_obj = BeautifulSoup(site, "html.parser")  # Get the html from the site
    for script in soup_obj(["script", "style"]):
        script.extract()  # Remove these two elements from the BS4 object
    company = soup_obj.find('span', {'class': 'company'})
    if company:
        company_name = company.get_text()
    # print company_name
    content = soup_obj.get_text()  # Get the text from this
    return content


def clean_up(dirty_data):
    """Clean up the dirty data."""
    clean_data = []
    for i in range(len(dirty_data)):
        temp = unicodedata.normalize('NFKD', "".join(dirty_data[i]).replace('\n', ' ').
                                     replace('\[[0-9]*\]', "").replace(' +', ' ').replace('\t', "").
                                     replace('\r', ' ')).encode('ascii', 'ignore')
        temp, sep, tail = temp.partition('Apply')
        clean_data.append(temp)
    return clean_data


def indeed_jobs(job=None, location=None):
    """Input the location's city and state and then look for the job in Indeed."""
    # Make sure the city specified works properly if it has more than one word (such as San Francisco)
    if job is not None:
        final_job = job.lower().replace(' ', '+')
        if location is not None:
            location_list = location.split(",", 1)
            city = location_list[0]
            state = location_list[1].strip().replace(' ', '+')
            final_city = city.split()
            final_city = '+'.join(word for word in final_city)
            final_site_list = 'http://www.indeed.ca/jobs?q=' + final_job + '&l=' + final_city + '%2C+' + state # Join all of our strings together so that indeed will search correctly
        else:
            final_site_list = ['http://www.indeed.ca/jobs?q="', final_job, '"']
    else:
        if location is not None:
            location_list = location.split(",", 1)
            city = location_list[0]
            state = location_list[1].strip().replace(' ', '+')
            final_city = city.split()
            final_city = '+'.join(word for word in final_city)
            final_site_list = 'http://www.indeed.ca/jobs?q=&l=' + final_city + '%2C+' + state # Join all of our strings together so that indeed will search correctly
        else:
            final_site_list = 'https://ca.indeed.com/jobs?q=&l=Nationwide'

    final_site = ''.join(final_site_list)  # Merge the html address together into one string
    base_url = 'https://www.indeed.ca/'
    # print(final_site_list, file=sys.stderr)

    try:
        html = urllib2.urlopen(final_site).read()  # Open up the front page of our search first
    except:
        'That city/state combination did not have any jobs. Exiting . . .'  # In case the city is invalid
        return
    soup = BeautifulSoup(html, "html.parser")  # Get the html from the first page

    # Now find out how many jobs there were
    div = soup.find(id='searchCount')
    # Now extract the total number of jobs found. The 'searchCount' object has this
    num_jobs_area = div.string.encode('utf-8')
    job_numbers = re.findall('\d+', num_jobs_area)  # Extract the total jobs found from the search result

    # print job_numbers
    if len(job_numbers) > 3:  # Have a total number of jobs greater than 1000
        total_num_jobs = (int(job_numbers[2]) * 1000) + int(job_numbers[3])
    else:
        total_num_jobs = int(job_numbers[2])
    city_title = city
    if city is None:
        city_title = 'Nationwide'

    # print 'There were', total_num_jobs, 'jobs found,', city_title  # Display how many jobs were found
    num_pages = total_num_jobs / 10
    # This will be how we know the number of times we need to iterate over each new search result page
    job_descriptions = []  # Store all our descriptions in this list
    final_URLs = []

    for i in xrange(0, num_pages):  # Loop through all of our search result pages
        # print 'Getting page', i
        start_num = str(i * 1)  # Assign the multiplier of 10 to view the pages we want
        current_page = ''.join([final_site, '&start=', start_num])
        # print "So that's the current page"
        # print current_page
        # Now that we can view the correct 10 job returns, start collecting the text samples from each
        html_page = urllib2.urlopen(current_page).read()  # Get the page
        page_obj = BeautifulSoup(html_page, "lxml")  # Locate all of the job links
        for script in page_obj(["script", "style"]):
            script.extract()

        # print "And that's the result col"
        job_link_area = page_obj.find(id='resultsCol')  # The center column on the page where the job postings exist
        job_URLS = [base_url + link.get('href') for link in job_link_area.find_all('a', href=True)]
        job_URLS = filter(lambda x: 'clk' in x, job_URLS)

        for j in xrange(0, len(job_URLS)):
            final_description = job_extractor(job_URLS[j])
            if final_description:  # So that we only append when the website was accessed correctly
                job_descriptions.append(final_description)
                final_URLs.append(job_URLS[j])

    new_job_desc = clean_up(job_descriptions)
    # code for database connectivity
    import sqlite3

    conn = sqlite3.connect('linked_deed.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS jobs_indeed')
    c.execute('CREATE TABLE jobs_indeed(ID INTEGER PRIMARY KEY AUTOINCREMENT, WHAT TEXT, URL TEXT, ACCURACY REAL, DESCRIPTION TEXT)')
    for i in range(len(job_descriptions)):
        c.execute('INSERT INTO jobs_indeed (ID, WHAT, URL, ACCURACY, DESCRIPTION) VALUES(?, ?, ?, ?, ?)', ((i + 1), job, final_URLs[i], 0.0, new_job_desc[i], ))
    conn.commit()
    c.close()
    conn.close()

    # print 'Done with collecting the job postings!'
    # print 'There were', len(job_descriptions), 'jobs successfully found.'


# indeed_jobs(job=job, location=location)
