#!/usr/bin/perl
#
# Helper script to get the architecture of the host system
# Part of the relinux toolkit
#
# Written by Anonymous Meerkat <meerkatanonymous@gmail.com>

use Dpkg::Arch get_raw_host_arch;

my $str = get_raw_host_arch();
if($str ne '')
{
	print get_raw_host_arch() . "\n";
	exit 0
} else {
	exit 1
}
