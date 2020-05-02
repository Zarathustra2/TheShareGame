"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

from rest_framework import serializers

from stats.models import KeyFigures, PastKeyFigures


class KeyFiguresSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFigures
        fields = ("book_value", "ttoc", "cdgr", "activity", "free_float", "share_price", "bid", "ask", "id")
        read_only_fields = fields


class PastKeyFiguresSerializer(serializers.ModelSerializer):
    class Meta:
        model = PastKeyFigures
        fields = ("book_value", "ttoc", "cdgr", "share_price", "activity", "free_float", "shares", "day", "id")
        read_only_fields = fields
