"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import django.core.checks


@django.core.checks.register("rest_framework.serializers")
def check_serializers(app_configs, **kwargs):
    """
    Custom checker for validating that all serializers have set read_only_fields.

    If all fields are available for write, then read_only_fields should be an empty tuple.

    Read_only serializers have a much better performance.

    Source: https://hakibenita.com/django-rest-framework-slow
    """

    import inspect
    from rest_framework.serializers import ModelSerializer
    import sys

    # Sometimes devs have not set up their IDE when optimizing imports
    # so the import could be accidentally removed, which will not import the serializers then.
    # Hence, we check if the module has been imported.
    if "tsg.urls" not in sys.modules:
        raise ValueError(
            "tsg.urls has not been imported! Likely it has been removed by your IDE when formatting the file?"
        )

    for serializer in ModelSerializer.__subclasses__():

        # Skip third-party apps.
        path = inspect.getfile(serializer)
        if path.find("site-packages") > -1:
            continue

        if hasattr(serializer.Meta, "read_only_fields"):
            continue

        yield django.core.checks.Warning(
            "ModelSerializer must define read_only_fields.",
            hint="Set read_only_fields in ModelSerializer.Meta",
            obj=serializer,
            id="H300",
        )


@django.core.checks.register("All Models have doc strings")
def check_models(app_configs, **kwargs):
    """
    Check each model has a docstring
    """

    from django.db import models
    import sys
    import inspect

    if "tsg.urls" not in sys.modules:
        raise ValueError(
            "tsg.urls has not been imported! Likely it has been removed by your IDE when formatting the file?"
        )

    for model in models.Model.__subclasses__():

        # Skip third-party apps.
        try:
            path = inspect.getfile(model)
        except TypeError:
            # Raises TypeError during tests because the model is a builtin fake
            # class
            continue
        if path.find("site-packages") > -1:
            continue

        if model.__doc__ is None:
            yield django.core.checks.Warning(
                "Each model requires a docstring", hint="Describe the model", obj=model, id="H301"
            )
