import pytest
from functools import partial
from scraper.scraper import Scraper


class TestScraper:
    @pytest.fixture
    def jobs(self):
        return [
            {"id": 1, "title": "Developer", "details": "Seeking full time developer"},
            {"id": 2, "title": "Software Developer", "details": ""},
            {"id": 3, "title": "Pharmacist", "details": ""},
            {"id": 4, "title": "Lion Tamer", "details": ""},
            {"id": 5, "title": "Chef", "details": ""},
            {"id": 6, "title": "Software Engineer", "details": "Seeking PHP dev"},
        ]

    def test_filter_results_w_no_filter(self, jobs):
        scpr = Scraper(["Developer"], ["Brisbane"], "www.job.com", "www.job.com")
        filtered_results = scpr.filter_results(jobs)
        assert filtered_results == jobs

    @pytest.mark.parametrize(
        "filters,expected_result",
        [
            (
                {"must_contain_terms": ["chef"]},
                [{"id": 5, "title": "Chef", "details": ""}],
            ),
            (
                {"must_contain_terms": ["engineer"], "must_not_contain_terms": ["PHP"]},
                [],
            ),
            (
                {"must_contain_one_of_terms": ["lion", "chef"]},
                [
                    {"id": 4, "title": "Lion Tamer", "details": ""},
                    {"id": 5, "title": "Chef", "details": ""},
                ],
            ),
        ],
    )
    def test_filter_results_w_filter(self, jobs, filters, expected_result):
        scpr = Scraper(
            ["Developer"], ["Brisbane"], "www.job.com", "www.job.com", filters=filters
        )
        filtered_results = scpr.filter_results(jobs)
        assert expected_result == filtered_results

    err_scpr = Scraper(["Developer"], ["Brisbane"], "www.job.com", "www.job.com")

    @pytest.mark.parametrize(
        "scpr_func",
        [
            err_scpr.get_jobs,
            partial(err_scpr.get_search_results, ""),
            partial(err_scpr.process_search_results, ""),
        ],
    )
    def test_scraper_errors(self, scpr_func):
        error_msg = "Not implemented in Scraper parent class. Please use child class for specific site."
        with pytest.raises(NotImplementedError, match=error_msg):
            scpr_func()
