"""
Google App Engine utilities
"""

def get_all_items(endpoint, params, http):
    """
    Get all items from a .list() command on an GAE endpoint.

    @param endpoint: gae endpoint
    @param http: httplib2.Http
    @return: list(dict)
    """

    items = []
    request = endpoint.list(**params)
    while request is not None:
        response = request.execute(http=http)
        items.extend(response.get('items', []))
        request = endpoint.list_next(request, response)

    return items
