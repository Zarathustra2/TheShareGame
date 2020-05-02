"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import logging

from django.db import transaction
from django.utils import timezone

from core.models import Activity, DepotPosition, Company
from stats.models import CompanyVolume, HistoryCompanyData, KeyFigures, PastKeyFigures
from tsg.const import CENTRALBANK
from users.models import Profile

logger = logging.getLogger(__name__)


def create_models_new_company(sender, instance, created, **kwargs):
    """
    Signal to create models upon company creation
    """

    if created:
        company = instance

        logger.info(
            f"Creating new objects for the new company {company}, cash: {company.cash}, shares: {company.shares}"
        )

        assert company.shares >= 1_000
        assert company.shares <= 1_000_000

        with transaction.atomic():
            time = timezone.now()

            Activity.objects.create(company_id=company.id)
            HistoryCompanyData.objects.create(company_id=company.id, start_shares=company.shares, joined=time)
            CompanyVolume.objects.create(company_id=company.id, day=time)

            if company.name != CENTRALBANK:
                DepotPosition.objects.create(depot_of=Company.get_centralbank(), company=company, amount=company.shares)

            book_value = company.cash
            share_price = company.cash / company.shares

            k = KeyFigures.objects.create(
                company_id=company.id,
                book_value=book_value,
                # On creation a company only has cash so ttoc equals the book value
                # for more explanation of the ttoc, please have a look at stats/models.py -> KeyFigures
                # and periodic_tasks/key_figures.py for the calculation.
                ttoc=book_value,
                share_price=share_price,
            )

            PastKeyFigures.past_from_current_key_figure(k).save()

            # set isin
            _id = company.id

            # TODO: Extract to method
            isin = f"{company.country}{'0' * (6 - len(str(_id)))}{_id}"

            logger.info(f"Setting isin: id was {_id}, country: {company.country}. ISIN => {isin}")

            company.isin = isin
            company.save()

            if company.user:
                try:
                    p = Profile.objects.get(user=company.user)
                except Profile.DoesNotExist:
                    logger.error(f"Profile does not exist for {company.user.id}")
                    return

                p.create_default_logo()
                p.save()
