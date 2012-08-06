/*
 * archdetect.c
 *
 * Architecture Detector for Python
 *
 *  Created on: 2012-08-05
 *      Author: Anonymous Meerkat
 */

// For now, we need to add this to use it
#define LIBDPKG_VOLATILE_API

#include <dpkg/arch.h>
#include <string.h>
#include <stdio.h>

#define GOOD 1
#define BAD 0

int getarch()
{
	char* str = get_raw_host_arch();
	if(strcmp(str, "") != 0)
	{
		printf(strcat(str, "\n"));
		return (GOOD);
	}
	else
	{
		return (BAD);
	}
}
