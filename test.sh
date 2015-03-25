#! /bin/bash

python -m doctest annotation.py
python -m doctest feature_template.py
python -m doctest feature_selection.py
python -m doctest feature_encoding.py
python -m doctest feature_extractor.py
python -m doctest tree_util.py
python -m doctest data.py
python -m doctest features.py
python -m doctest ling_util.py
python -m doctest dependency_path.py
