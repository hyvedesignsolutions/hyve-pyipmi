#/bin/bash
echo "[1/4] Cleaning the working space..."
git clean -xfd
echo
echo "[2/4] Packing the release code..."
python3 setup.py sdist bdist_wheel
echo
echo "[3/4] Listing the files to be released..."
ls dist
echo
echo "[4/4] Releasing the code..."
read -n 1 -s -r -p "Press any key to continue...."
twine upload dist/*

