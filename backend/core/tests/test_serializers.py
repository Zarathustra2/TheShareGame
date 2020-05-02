from common.test_base import BaseTestCase

from core.serializers import BondSerializer


class BondSerializerTestCase(BaseTestCase):
    def test_company_isin_is_required(self):
        data = {"value": 10000, "runtime": 3}
        serializer = BondSerializer(data=data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertTrue("company_isin" in serializer.errors)

    def test_value_cannot_be_negative(self):
        data = {"value": -1, "runtime": 2, "company_isin": self.company.isin}
        serializer = BondSerializer(data=data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertTrue("value" in serializer.errors)

    def test_runtime_cannot_be_negative(self):
        data = {"value": 10000, "runtime": -1, "company_isin": self.company.isin}
        serializer = BondSerializer(data=data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertTrue("runtime" in serializer.errors)

    def test_runtime_cannot_be_greater_than_three(self):
        data = {"value": 10000, "runtime": 4, "company_isin": self.company.isin}
        serializer = BondSerializer(data=data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertTrue("runtime" in serializer.errors)

    def test_company_needs_to_have_enough_money(self):
        data = {"value": self.company.cash + 1, "runtime": 3, "company_isin": self.company.isin}
        serializer = BondSerializer(data=data)
        self.assertEqual(serializer.is_valid(), False)
        self.assertTrue("value" in serializer.errors)
