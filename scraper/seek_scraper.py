import requests
from bs4 import BeautifulSoup
from scraper.scraper import Scraper

class SeekScraper(Scraper):
    
    def __init__(self, job_titles, locations, filters=None):
        search_url = "https://www.seek.com.au/{title}-jobs/in-{location}"
        job_url = "https://www.seek.com.au/job/{id}"
        
        super(SeekScraper, self).__init__(job_titles, locations, search_url, job_url, filters)
    
    
    def get_search_results(self, search_url):
        page = 1
        job_ids = []

        while (True):
            url = search_url + "?page={}".format(page)
            
            data = requests.get(url)
            soup = BeautifulSoup(data.content, "html.parser")

            if (soup.find(attrs={"data-automation":"searchZeroResults"})):
                print("All available pages processed")
                break  
            else:
                print("Processing search results page {}".format(page))
                job_ids += [item['data-job-id'] for item in soup.find_all('article', attrs={'data-job-id': True})]
                page += 1 

        return job_ids
        
        
    def get_job_details(self, job_id):
        url = self.job_url_template.format(id=job_id)
        data = requests.get(url)
        soup = BeautifulSoup(data.content, "html.parser")

        details_container = soup.find(attrs={"data-automation":"job-detail-page"})

        if details_container:
            detail_selectors = {
                "title": {"data-automation": "job-detail-title"},
                "advertiser_name": {"data-automation": "advertiser-name"},
                "work_type": {"data-automation": "job-detail-work-type"},
                "details": {"data-automation": "jobAdDetails"},
            }

            details={
                "job_id": job_id,
                "url": url
            }
            
            for detail, path in detail_selectors.items():
                results = [item.get_text() for item in soup.find_all(attrs=path)]
                details[detail] = ' '.join(results)
        
            return details


    def process_search_results(self, job_ids):
        results = []
        for id in job_ids:
            job_details = self.get_job_details(id)
            results += [job_details] if job_details is not None else []
            print("Retrieved details for {} job(s)".format(len(results)))
            
        return results