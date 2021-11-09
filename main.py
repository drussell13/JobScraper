import csv
from scraper.seek_scraper import SeekScraper

seek_job_titles = ["psychologist"]

seek_locations = ["All-Brisbane-QLD", 
             "East-Ipswich-QLD-4305", 
             "Ipswich-QLD-4305", 
             "Western-Suburbs-&-Ipswich-Brisbane-QLD",
             "Southern-Suburbs-&-Logan-Brisbane-QLD",
             "All-Gold-Coast-QLD"]

filters = {
    "must_contain_terms": ["psychologist"],
    "must_not_contain_terms": ["lecturer", "senior", "postdoctoral", "physiologist", "medicare", "hervey bay"],
    "must_contain_one_of_terms": ["provisional", "4+2", "4 + 2", "internship"]   
}   


def output_results(results):
    previously_retrieved_jobs = get_previously_retrieved_jobs()
    new_jobs_found = []
    
    with open("job_listings.csv", 'w') as f:   
        column_labels = ["ID", "Title", "Type", "URL"]
        f.write(', '.join(column_labels))
        f.write('\n')

        for result in results:
            
            if result["job_id"] not in previously_retrieved_jobs:
                new_jobs_found.append("Title - {}, Type - {}, URL - {}"
                                             .format(result["title"], result["work_type"], result["url"]))

            row_data = [result["job_id"],
                        result["title"].replace(',', '').replace(';', ''),  # need to remove or will break csv 
                        result["work_type"],
                        result["url"].replace(',', '').replace(';', '')]

            f.write(', '.join(row_data))
            f.write('\n')
    
    if new_jobs_found:
        print("\n======== {} NEW JOBS FOUND ========".format(len(new_jobs_found)))
        print(*new_jobs_found, sep='\n')
    else:
        print("\n======== NO NEW JOBS FOUND ¯\_(ツ)_/¯  ========\n")


def get_previously_retrieved_jobs():
    try:
        with open("job_listings.csv", "r") as f:
            if f:
                reader = csv.reader(f)
                return [job[0] for job in reader]
    except Exception as e:
        return []


def main():
    total_jobs_found = []
    
    seek_scrpr = SeekScraper(job_titles=seek_job_titles, locations=seek_locations, filters=filters)
    total_jobs_found += seek_scrpr.get_jobs()
    
    output_results(total_jobs_found)


if __name__ == "__main__":
    main()