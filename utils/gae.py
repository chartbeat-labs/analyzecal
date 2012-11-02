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

def get_cal_name(cal_id, service, http):
    """
    Retrieve the name (summary) for a calendar.

    @param cal_id: str, calendar id
    @return: str, calendar name
    """

    response = service.calendars().get(calendarId=cal_id).execute(http=http)
    return response['summary']
