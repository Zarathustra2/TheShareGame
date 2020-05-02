"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from celery import shared_task

from core.models import Bond, Company, InterestRate


@shared_task()
def create_bond(value, company_isin, runtime) -> Bond:
    """
    Celery-Task for buying a bond.

    :param value:
    :param company_isin:
    :param runtime:
    :return:

    TODO: Actually not needed. Delete it!
    """
    rate = InterestRate.calc_rate(value)
    company_id = Company.get_id_from_isin(company_isin)
    bond = Bond.objects.create(company_id=company_id, value=value, rate=rate, runtime=runtime)

    return bond
