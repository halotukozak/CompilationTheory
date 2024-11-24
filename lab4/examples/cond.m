x = 5;

if (x == 5) {
    print "x is 5";     
}
if (x== 7) {
    print "x is 7";
}

while (x > 0) {
    for i = 0:2 {
        if (i == 1) {
            continue;
        }
        print "i:", i;
    }
}