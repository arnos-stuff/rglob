#!/bin/bash

for i in 2 4 6 8 10 12 14
do
	 rglob xrg 0:5:0.01 | rglob tf map "(x + 0.00001
)**(-$i/20) - 1" | rglob tf join , >> example.csv
done

 rglob xrg 0:5:0.01 | rglob tf map "np.log(x)" | rglob tf join , >> example.csv
 rglob xrg 0:5:0.01 | rglob tf join ,  >> example.csv
