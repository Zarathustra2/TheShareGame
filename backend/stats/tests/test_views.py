"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

# Create your tests here.

from freezegun import freeze_time
from rest_framework.reverse import reverse

from common.test_base import NOW, BaseTestCase
from stats.models import PastKeyFigures


@freeze_time(NOW)
class PastKeyFiguresApiTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        # We have a singal which triggers on creation of a company.
        # The signal creates a PastKeyFigure model on creation.
        # So we update the model with our data for testing purpose
        self.key_figure, _ = PastKeyFigures.objects.update_or_create(
            company=self.company,
            defaults={
                "ttoc": 100000,
                "book_value": 100000,
                "cdgr": 1,
                "free_float": 75,
                "activity": 50,
                "day": NOW,
                "shares": 10000,
                "share_price": 5,
            },
        )

    def test_url(self):
        """Test the GET method for the past_key_figures url of a company"""
        url = reverse("stats:past_key_figures", kwargs={"isin": self.company.isin})
        client = self.client
        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        should_be = [
            {
                "book_value": 100000.00,
                "ttoc": 100000.00,
                "cdgr": 1.00,
                "share_price": 5.00,
                "activity": 50,
                "free_float": 75.00,
                "shares": 10000,
                "day": NOW.strftime("%Y-%m-%d"),
                "id": self.key_figure.id,
            }
        ]

        self.assertListEqual(should_be, response.json())
