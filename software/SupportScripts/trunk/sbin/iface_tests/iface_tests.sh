#!/bin/bash

echo Running tests for rbc_iface_patch.py. Results must be manually
echo verified, for now. Future versions of this test will automate this.
echo
echo 1. Adding eth0:0 interface as static with no gateway
cp -f interfaces1 interfaces1_test
python ../rbc_iface_patch.py -f interfaces1_test -t static -i 192.168.10.1 eth0:0
diff -u interfaces1 interfaces1_test

echo ----------------------------------------------------------------------

echo 2. Converting eth0 from dhcp to static
cp -f interfaces2 interfaces2_test
python ../rbc_iface_patch.py -f interfaces2_test -t static -i 192.168.1.50 -g 192.168.1.1 eth0
diff -u interfaces2 interfaces2_test

echo ----------------------------------------------------------------------

echo 3. Converting eth0 from static to dhcp
cp -f interfaces3 interfaces3_test
python ../rbc_iface_patch.py -f interfaces3_test -t dhcp eth0
diff -u interfaces3 interfaces3_test

echo ----------------------------------------------------------------------

echo 4. Changing eth0 from dhcp to dhcp. No patch should appear.
cp -f interfaces4 interfaces4_test
python ../rbc_iface_patch.py -f interfaces4_test -t dhcp eth0
diff -u interfaces4 interfaces4_test

echo ----------------------------------------------------------------------

echo 5. Removing wlan0 interface from file which does not have it. No patch again.
cp -f interfaces5 interfaces5_test
python ../rbc_iface_patch.py -f interfaces5_test -r wlan0
diff -u interfaces5 interfaces5_test

echo ----------------------------------------------------------------------

echo 6. Removing wlan0 interface from file which does have it.
cp -f interfaces6 interfaces6_test
python ../rbc_iface_patch.py -f interfaces6_test -r wlan0
diff -u interfaces6 interfaces6_test

echo ----------------------------------------------------------------------

echo 7. Removing wlan0 interface from file where it was not an auto interface.
cp -f interfaces7 interfaces7_test
python ../rbc_iface_patch.py -f interfaces7_test -r wlan0
diff -u interfaces7 interfaces7_test

echo ----------------------------------------------------------------------

echo 8. Converting eth0 from dhcp to static in a file with no blank lines.
cp -f interfaces8 interfaces8_test
python ../rbc_iface_patch.py -f interfaces8_test -t static -i 192.168.1.50 -g 192.168.1.1 eth0
diff -u interfaces8 interfaces8_test

echo ----------------------------------------------------------------------

echo 9. Removing ath0 from an interfaces file with no blank lines.
cp -f interfaces9 interfaces9_test
python ../rbc_iface_patch.py -f interfaces9_test -r ath0
diff -u interfaces9 interfaces9_test

echo ----------------------------------------------------------------------

echo 10. Removing ath0 from an interfaces file with double blank lines.
cp -f interfaces10 interfaces10_test
python ../rbc_iface_patch.py -f interfaces10_test -r ath0
diff -u interfaces10 interfaces10_test

echo ----------------------------------------------------------------------

echo 11. Editing eth0 from an interfaces file with no blank lines
cp -f interfaces11 interfaces11_test
python ../rbc_iface_patch.py -f interfaces11_test -t dhcp eth0
diff -u interfaces11 interfaces11_test

echo ----------------------------------------------------------------------

rm -f interfaces*_test
echo "All done!"
