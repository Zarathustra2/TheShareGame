"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from django.db import connection, reset_queries
import logging
import time

logger = logging.getLogger(__name__)


class RequestTimeMiddleware:
    """
    Custom Middleware to log how long it takes to generate
    a response for a request
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = request.get_full_path()
        request.time = time.time()

        response = self.get_response(request)

        time_taken = time.time() - request.time
        if time_taken > 0.8:
            logger.error(f"Time taken for {url}: {time_taken}")

        return response


class QueryCountDebugMiddleware:
    """
    This middleware will log the number of queries run
    and the total time taken for each request (with a
    status code of 200).

    Source: https://gist.github.com/daniestrella1/869b664b08e11615f542814f39ca6f15
    """

    # Set this to true to print all executed queries of the connection
    # This is helpful during debugging which queries have been run
    # during an api call.
    PRINT_QUERIES = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        reset_queries()
        response = self.get_response(request)

        if response.status_code == 200:
            total_time = 0

            url = request.get_full_path()

            for query in connection.queries:
                query_time = query.get("time")
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get("duration", 0) / 1000
                total_time += float(query_time)

            logger.info("Url: %s => %s queries run in %s seconds" % (url, len(connection.queries), total_time))

            if self.PRINT_QUERIES:
                for query in connection.queries:
                    logger.info(query)

        return response
