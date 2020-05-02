"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging
from typing import Union

from django.db.models import QuerySet
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class BaseListAPIServerSide:
    """
    Mixin for ListApiViews.

    Required to work with server-side table rendering.
    """

    default_ordering = "-id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.get_queryset, "is_overridden"):
            logger.warning(
                "Do not override the get_queryset() method from the BaseListAPIServerSide. "
                "Override get_queryset_list() instead!"
            )

    def get_queryset(self) -> QuerySet:
        qs = self.get_queryset_list()
        if qs is None:
            qs = super().get_queryset()

        order = self.get_order()

        if not isinstance(order, str):
            logger.warning(f"{order} not of type str")
            order = "id"

        return qs.order_by(order).filter(**self.get_filter_kwargs())

    def get_queryset_list(self) -> Union[QuerySet, None]:
        """If you need to override the get_queryset method, override this"""
        return None

    def get_order(self) -> str:
        # asc and desc is handled on the clients side
        # they will add an '-' if they require descending ordering
        order = self.request.GET.get("sort", False)

        if order is False:
            return self.default_ordering

        # Check if the field can be used for sorting
        field = order.replace("-", "")
        if field not in self.get_fields_sortable():
            logger.info(f"{field} not a sortable field")
            return self.default_ordering

        return order

    def search(self, search_value) -> None:
        """Filters the queryset by the search value"""
        # ToDo: Column based searching
        pass

    def get_filter_kwargs(self) -> dict:
        return {}

    def get_fields_sortable(self) -> [str]:
        """
        Returns a list of fields which can be used for .order_by()
        """
        return ["id"]


class PaginatedResponseMixin:
    def get_paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
