window.BENCHMARK_DATA = {
  "lastUpdate": 1598265101382,
  "repoUrl": "https://github.com/philipschoemig/BER-TLV",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "philip.schoemig@posteo.de",
            "name": "Philip Schömig",
            "username": "philipschoemig"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2a53b04d089fd5c33f977c75018692bfa90d6dc6",
          "message": "Update tests.yml",
          "timestamp": "2020-08-24T08:57:59+02:00",
          "tree_id": "01959aae6effc17efc2449addf38645758f9a74c",
          "url": "https://github.com/philipschoemig/BER-TLV/commit/2a53b04d089fd5c33f977c75018692bfa90d6dc6"
        },
        "date": 1598252322081,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_stream.py::TestBufferedStream::test_is_eof",
            "value": 1917524.9710435423,
            "unit": "iter/sec",
            "range": "stddev: 4.684803366328201e-7",
            "extra": "mean: 521.505594503829 nsec\nrounds: 149254"
          },
          {
            "name": "tests/test_stream.py::TestBufferedStream::test_size",
            "value": 3312095.7217053515,
            "unit": "iter/sec",
            "range": "stddev: 7.159647548683791e-7",
            "extra": "mean: 301.92364110935597 nsec\nrounds: 196079"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "philip.schoemig@posteo.de",
            "name": "Philip Schömig",
            "username": "philipschoemig"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b52acf485dd437b734c09acf18336b8f32e7619d",
          "message": "Update tests.yml",
          "timestamp": "2020-08-24T12:30:47+02:00",
          "tree_id": "33aca0bebca2f60c097d9b19325f984a25faa084",
          "url": "https://github.com/philipschoemig/BER-TLV/commit/b52acf485dd437b734c09acf18336b8f32e7619d"
        },
        "date": 1598265100944,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_stream.py::TestBufferedStream::test_is_eof",
            "value": 1438005.1675077316,
            "unit": "iter/sec",
            "range": "stddev: 9.68545690780301e-7",
            "extra": "mean: 695.4077930979503 nsec\nrounds: 131579"
          },
          {
            "name": "tests/test_stream.py::TestBufferedStream::test_size",
            "value": 2424495.6322252303,
            "unit": "iter/sec",
            "range": "stddev: 9.078277353886573e-7",
            "extra": "mean: 412.45691957852574 nsec\nrounds: 192271"
          }
        ]
      }
    ]
  }
}