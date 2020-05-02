"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from rest_framework.generics import ListAPIView

from core.models import Company
from stats.models import PastKeyFigures
from stats.serializers import PastKeyFiguresSerializer


class PastKeyFiguresListApiView(ListAPIView):
    """
    Returns the PastKeyFigures of a company given by isin
    """

    serializer_class = PastKeyFiguresSerializer
    queryset = PastKeyFigures.objects.all()

    def get_queryset(self):
        isin = self.kwargs.get("isin")
        id_ = Company.get_id_from_isin(isin)
        return super().get_queryset().filter(company_id=id_).order_by("day")
