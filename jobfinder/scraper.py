class Scraper:
    def __init__(self, job_titles, locations, search_url_tmplt, job_url_tmplt):
        self.job_titles = job_titles
        self.locations = locations
        self.search_url_template = search_url_tmplt
        self.job_url_template = job_url_tmplt
        
    def scrape_jobs(self): 
        raise NotImplementedError()
