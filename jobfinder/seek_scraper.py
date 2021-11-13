import requests
import itertools
from bs4 import BeautifulSoup
from jobfinder.scraper import Scraper

class SeekScraper(Scraper):
    
    def __init__(self, job_titles, locations):
        search_url_tmplt = "https://www.seek.com.au/{}-jobs/in-{}"
        job_url_tmplt = "https://www.seek.com.au/job/{}"
        
        super(SeekScraper, self).__init__(job_titles, locations, search_url_tmplt, job_url_tmplt)
    
    
    def scrape_jobs(self):
        
        # Step 1 - Retrieve list of job_ids from the search 
        
        search_results = []
        search_query_combinations = list(itertools.product(self.job_titles, self.locations))
        for comb in search_query_combinations:
            url = self.search_url_template.format(*comb)
            
            print("Searching - {}".format(url))
            search_results += self.__get_search_results(url)

        search_results = list(set(search_results))  # remove duplicates 
        search_results.sort()

        print("\nFound {} possible jobs!\n".format(len(search_results)))

        # Step 2 - Retrieve details for each of the jobs found in search and return

        return self.__process_search_results(search_results)
        
    
    def __get_search_results(self, search_url):
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
        
        
    def __get_job_details(self, job_id):
        url = self.job_url_template.format(job_id)
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


    def __process_search_results(self, job_ids):
        results = []
        for id in job_ids:
            job_details = self.__get_job_details(id)
            results += [job_details] if job_details is not None else []
            print("Retrieved details for {} job(s)".format(len(results)))
        
        return results