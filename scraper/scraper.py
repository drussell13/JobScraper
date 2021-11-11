class Scraper:
    
    def __init__(self, job_titles, locations, search_url_tmplt, job_url_tmplt, filters=None):
        self.job_titles = job_titles
        self.locations = locations
        self.search_url_template = search_url_tmplt
        self.job_url_template = job_url_tmplt
        self.filters = self.__decapitalise_filters(filters)
    
    
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
        raise NotImplementedError("Not implemented in Scraper parent class. Please use child class for specific site.")
    
    
    def process_search_results(self, job_ids):
        raise NotImplementedError("Not implemented in Scraper parent class. Please use child class for specific site.")
    
    
    def filter_results(self, results):
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