#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
int main(int argc, char *argv[])
{
    int pid;
    setuid(0);
    if (argc != 1)
    {
        if (strcmp(argv[1],"stop") == 0)
        {
            system("killall wvdial &> /dev/null");
            return 0;
        }
    }
    else
    {
        pid = fork();
        if (pid == 0)
            system("wvdial &> /dev/null");
    }
    return 0;
}
