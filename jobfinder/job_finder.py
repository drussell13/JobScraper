class JobFinder:
    def __init__(self, scrapers, filters=None):
        self.scrapers = scrapers
        self.filters = self.__decapitalise_filters(filters)
    
    
    def get_jobs(self):
        jobs = []
        for scraper in self.scrapers:
            jobs += scraper.scrape_jobs()
        
        jobs = self.__filter_results(jobs)
        return jobs
        

    def __filter_results(self, results):
        return [job for job in results if self.__job_passes_filter(job)]
    
    
    def __job_passes_filter(self, job_details):
        must_contain_terms = self.filters.get("must_contain_terms", [])
        for term in must_contain_terms:
            filter_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
            if not filter_satisfied:
                return False

        must_not_contain_terms = self.filters.get("must_not_contain_terms", [])
        for term in must_not_contain_terms:
            filter_not_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
            if filter_not_satisfied:
                return False

        must_contain_one_of_terms = self.filters.get("must_contain_one_of_terms", [])
        if must_contain_one_of_terms:
            filter_satisfied = False
            for term in must_contain_one_of_terms:
                if term in job_details["title"].lower() or term in job_details["details"].lower():
                    filter_satisfied = True
                    break
            
            if not filter_satisfied:
                return False
        
        return True


    def __decapitalise_filters(self, filters):
        if filters:
            return {
                key: [item.lower() for item in val] for key, val in filters.items() 
            }
        else:
            return {}