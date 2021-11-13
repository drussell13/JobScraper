import pytest
from jobfinder.job_finder import JobFinder


class TestJobFinder:
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
        job_finder = JobFinder(None, None)
        filtered_results = job_finder._JobFinder__filter_results(jobs)
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
        job_finder = JobFinder(None, filters)
        filtered_results = job_finder._JobFinder__filter_results(jobs)
        assert filtered_results == expected_result
