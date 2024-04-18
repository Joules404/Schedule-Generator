curl -o classes.txt https://uisapppr3.njit.edu/scbldr/include/datasvc.php?p=/
tail -c +16 classes.txt | head -c -53 > classes_modified.txt