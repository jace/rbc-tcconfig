#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

int main()
{
  setuid(0);
  system("cat >/etc/cups/printers.conf");
  system("/etc/init.d/cupsys restart");
  return 0;
}
