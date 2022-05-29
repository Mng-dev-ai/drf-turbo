**********************
Performance Benchmarks
**********************

Using Pydantic's benchmarking code, drf-turbo performs serialization, deserialization and validation nearly
*eight times faster* than a standard django-rest-framework configuration.

You can see a closed pull request to add this benchmarking code to Pydantic `here <https://github.com/samuelcolvin/pydantic/pull/3404>`_

.. csv-table::
       :header: "Package", "Version", "Relative Performance", "Mean Validation Time"

        "drf-turbo","0.1.1","","113.79μs"
        "django-rest-framework","3.12.4","7.78x slower","885.47μs"

See `Pydantic benchmarking page <https://pydantic-docs.helpmanual.io/benchmarks/>`_ for more relative performance data
and of the a link to the benchmarking code.


Raw scores:
::

          drf-turbo best=111.754μs/iter avg=113.794μs/iter stdev=1.274μs/iter version=0.1.1
          django-rest-framework best=856.090μs/iter avg=885.471μs/iter stdev=39.377μs/iter version=3.12.4
          pydantic best=103.525μs/iter avg=106.093μs/iter stdev=2.720μs/iter version=1.8.2
          attrs + cattrs best=67.449μs/iter avg=67.766μs/iter stdev=0.388μs/iter version=21.2.0
          cerberus best=1561.922μs/iter avg=1638.844μs/iter stdev=44.257μs/iter version=1.3.4
          marshmallow best=198.683μs/iter avg=201.499μs/iter stdev=2.192μs/iter version=3.14.0
          valideer best=90.025μs/iter avg=91.712μs/iter stdev=1.579μs/iter version=0.4.2
          voluptuous best=195.394μs/iter avg=197.416μs/iter stdev=2.399μs/iter version=0.12.2
          schematics best=728.707μs/iter avg=745.313μs/iter stdev=11.523μs/iter version=2.1.1
          trafaret best=221.880μs/iter avg=223.723μs/iter stdev=1.050μs/iter version=2.1.0

