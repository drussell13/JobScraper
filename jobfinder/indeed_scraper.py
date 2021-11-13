import requests
from itertools import product
from bs4 import BeautifulSoup
from jobfinder.scraper import Scraper

class IndeedScraper(Scraper):
    
    def __init__(self, job_titles, locations):
        search_url_tmplt = "https://au.indeed.com/jobs?q={}&l={}"
        job_url_tmplt = "https://au.indeed.com/viewjob?jk={}"
            
        super(IndeedScraper, self).__init__(job_titles, locations, search_url_tmplt, job_url_tmplt)
    
    
    def scrape_jobs(self):
        
        # Step 1 - Retrieve list of job_ids from the search 
        
        search_results = []
        search_query_combinations = list(product(self.job_titles, self.locations))
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
            url = search_url + "&start={}".format((page-1)*10)  # page indexing on indeed is weird... page 35 = 340 in url
            
            data = requests.get(url)
            soup = BeautifulSoup(data.content, "html.parser")

            indeed_search_results_info = soup.find("div", {"id": "searchCountPages"}).get_text().strip()
            indeed_page_counter = int(indeed_search_results_info.split(' ')[1])
            if (indeed_page_counter < page):
                print("All available pages processed")
                break  
            else:
                print("Processing search results page {}".format(page))
                job_ids += [item['data-jk'] for item in soup.find_all('a', attrs={'data-jk': True})]
                page += 1 

        print(job_ids)

        return job_ids
        
        
    def __get_job_details(self, job_id):
        url = self.job_url_template.format(job_id)
        data = requests.get(url)
        soup = BeautifulSoup(data.content, "html.parser")

        details_container = soup.find("div", {"class":"jobsearch-JobComponent"})

        if details_container:
            detail_selectors = {
                "title": ("div", {"class":"jobsearch-JobInfoHeader-title-container"}),
                "advertiser_name": ("div", {"class":"jobsearch-JobInfoHeader-subtitle"}),
                "work_type": ("div", {"class":"jobsearch-JobMetadataHeader-item"}),
                "details": ("div", {"class":"jobsearch-JobComponent-description"}),
            }

            details={
                "job_id": job_id,
                "url": url
            }
            
            for detail, path in detail_selectors.items():
                results = [item.get_text() for item in soup.find_all(*path)]
                details[detail] = ' '.join(results)
        
            return details


    def __process_search_results(self, job_ids):
        results = []
        for id in job_ids:
            job_details = self.__get_job_details(id)
            results += [job_details] if job_details is not None else []
            print("Retrieved details for {} job(s)".format(len(results)))
        
        return results