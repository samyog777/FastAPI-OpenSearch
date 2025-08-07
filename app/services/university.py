from app.services.base_opensearch import BaseOpenSearchService


class UniversityService(BaseOpenSearchService):
    def __init__(self):
        mappings = {
            "name": {"type": "text"},
            "country": {"type": "text"},
            "state_province": {"type": "text"},
            "domains": {"type": "text"},
            "web_pages": {"type": "text"},
            "alpha_two_code": {"type": "text"},
        }
        super().__init__(index_name="universities", mappings=mappings)


university_service = UniversityService()
