#!   /bin/bash -e
n=$(ls rdfData/|wc -l)
k=$(($n / 1000))
echo "Packing $n files $k packages"
for ((z=0;z<=k;z++))
do
     fn="kenom_p_$z.zip"
     rm -f "$fn"
     w=$(ls rdfData/|grep "_0$z[0-9]" |wc -l)
     echo "pack $w files in file $fn"
     #ls rdfData/*.ttl|grep "_01[0-9]" | zip a.zip -@ -q
     ls rdfData/*.ttl|grep "_0$z[0-9]" | zip "$fn" -@ -q
done
