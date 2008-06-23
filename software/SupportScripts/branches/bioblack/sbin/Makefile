# Makefile for support script helpers
# Must be run as root for make perms.
# Doesn't handle install/uninstall,
# as that is done via the binary packages.

all: rbc_printers_reconfigure rbc_dialer

rbc_printers_reconfigure:
	gcc rbc_printers_reconfigure.c -o rbc_printers_reconfigure

rbc_dialer:
	gcc rbc_dialer.c -o rbc_dialer

perms:
	chown root:www-data rbc_printers_reconfigure
	chmod 550 rbc_printers_reconfigure
	chmod u+s rbc_printers_reconfigure
	chmod 550 rbc_dialer
	chmod u+s rbc_dialer

clean:
	rm -f rbc_printers_reconfigure
	rm -f rbc_dialer
