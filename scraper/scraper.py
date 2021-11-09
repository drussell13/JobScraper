class Scraper:
    
    def __init__(self, job_titles, locations, search_url, job_url, filters=None):
        self.job_titles = job_titles
        self.locations = locations
        self.filters = filters
        self.search_url_template = search_url
        self.job_url_template = job_url
        
        
    def get_jobs(self):
        
        # Step 1 - Retrieve list of job_ids from the search 
        
        search_results = []
        for title in self.job_titles:
            for loc in self.locations:
                url = self.search_url_template.format(title=title, location=loc)
                print("Searching - {}".format(url))
                search_results += self.get_search_results(url)

        search_results = list(set(search_results))
        search_results.sort()

        print("\nFound {} possible jobs!\n".format(len(search_results)))

        # Step 2 - Check each job from search result and return those that pass our filters

        results = self.process_search_results(search_results)
        
        return self.filter_results(results)
        
        
    def get_search_results(self, search_url):
        pass  # Implement in child class based on particular site 
    
    
    def process_search_results(self, job_ids):
        pass  # Implement in child class based on particular site 
    
    
    def filter_results(self, results):
        return [job for job in results if self.job_passes_filter(job)]
    
    
    def job_passes_filter(self, job_details):
        must_contain_terms = self.filters["must_contain_terms"]
        for term in must_contain_terms:
            filter_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
            if not filter_satisfied:
                return False

        must_not_contain_terms = self.filters["must_not_contain_terms"]
        for term in must_not_contain_terms:
            filter_not_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
            if filter_not_satisfied:
                return False

        must_contain_one_of_terms = self.filters["must_contain_one_of_terms"]
        filter_satisfied = False
        for term in must_contain_one_of_terms:
            if term in job_details["title"].lower() or term in job_details["details"].lower():
                filter_satisfied = True
                break

        return filter_satisfied