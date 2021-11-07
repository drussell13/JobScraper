import requests
from bs4 import BeautifulSoup


job_titles = ["psychologist-internship", "psychologist-intern"]
locations = ["All-Brisbane-QLD"]

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
            "id": id,
            "url": url
        }
        
        for detail, path in detail_selectors.items():
            results = [item.get_text() for item in soup.find_all(attrs=path)]
            details[detail] = ' '.join(results)
    
        return details


def job_passes_filter(job_details):
    filter_satisfied = False

    search_terms = ["graduate", "registrar", "provisional", "internship", "4+2"]

    for term in search_terms:
        if term in job_details["title"].lower() or term in job_details["details"].lower():
            filter_satisfied = True
            break

    return filter_satisfied


def scrape(search_url):
    job_ids = get_search_results(search_url)

    results = []    
    for id in job_ids:
        print("Processing job with id {}".format(id))

        job_details = get_job_details(id)
    
        if job_details is not None and job_passes_filter(job_details):
            results.append(job_details)

    return results


def output_results(results):
    with open("job_listings.csv", 'w') as f:   
        column_labels = ["Type", "Title", "URL"]
        f.write(', '.join(column_labels))
        f.write('\n')

        print("\n======== RESULTS FOUND ========")
        for result in results:
            print("Title - {}, Type - {}, URL - {}".format(result["title"], result["work_type"], result["url"]))

            row_data = [result["work_type"], 
                        result["title"].replace(',', ''),  # need to remove or will break csv 
                        result["url"].replace(',', '')]

            f.write(', '.join(row_data))
            f.write('\n')


def main():
    total_results = []
    for title in job_titles:
        for loc in locations:
            search_url = seek_search_url.format(title=title, location=loc)
            total_results += scrape(search_url)  # add in smarts for dup checking

    output_results(total_results)


if __name__ == "__main__":
    main()