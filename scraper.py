import sys
import csv
import requests
from bs4 import BeautifulSoup


job_titles = ["psychologist"]

locations = ["All-Brisbane-QLD", 
             "East-Ipswich-QLD-4305", 
             "Ipswich-QLD-4305", 
             "Western-Suburbs-&-Ipswich-Brisbane-QLD",
             "Southern-Suburbs-&-Logan-Brisbane-QLD",
             "All-Gold-Coast-QLD"]

seek_search_url = "https://www.seek.com.au/{title}-jobs/in-{location}"
seek_job_url = "https://www.seek.com.au/job/{id}"

def get_search_results(search_url):
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


def get_job_details(job_id):
    url = seek_job_url.format(id=job_id)
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


def job_passes_filter(job_details):
    
    must_contain_terms = ["psychologist"]
    for term in must_contain_terms:
        filter_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
        if not filter_satisfied:
            return False

    must_not_contain_terms = ["lecturer", "senior", "postdoctoral", "physiologist", "medicare", "hervey bay"]
    for term in must_not_contain_terms:
        filter_not_satisfied = term in job_details["title"].lower() or term in job_details["details"].lower()
        if filter_not_satisfied:
            return False

    must_contain_one_of_terms = ["provisional", "4+2", "4 + 2", "internship"]
    filter_satisfied = False
    for term in must_contain_one_of_terms:
        if term in job_details["title"].lower() or term in job_details["details"].lower():
            filter_satisfied = True
            break

    return filter_satisfied


def process_search_results(job_ids):
    results = []
    total_rows_processed = 0    
    
    for id in job_ids:
        job_details = get_job_details(id)
    
        if job_details is not None and job_passes_filter(job_details):
            results.append(job_details)

        total_rows_processed += 1
        print("Processed {} row(s), {} jobs found".format(total_rows_processed, len(results)))

    return results


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
    
    # Step 1 - Compile list of job_ids from Seek search results
    
    search_results = []
    for title in job_titles:
        for loc in locations:
            search_url = seek_search_url.format(title=title, location=loc)
            print("Searching - {}".format(search_url))
            search_results += get_search_results(search_url)

    search_results = list(set(search_results))
    search_results.sort()

    print("\nFound {} possible jobs!\n".format(len(search_results)))

    # Step 2 - Check each job from search result and return those that pass our filters

    results = process_search_results(search_results)

    output_results(results)
    

if __name__ == "__main__":
    main()