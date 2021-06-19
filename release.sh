#/bin/bash
echo "Cleaning the working space..."
git clean -xfd
echo "Packing the release code..."
python3 setup.py sdist bdist_wheel
echo "Listing the packages to be released..."
ls dist
echo "Releasing the code..."
read -n 1 -s -r -p "Press any key to continue...."
twine upload dist/*

