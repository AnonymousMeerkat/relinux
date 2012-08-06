#!/bin/bash
# Generic SWIG build script for relinux
# Anonymous Meerkat <meerkatanonymous@gmail.com>

. ./buildconfig

# DO NOT EDIT BELOW THIS LINE
##############################

diec() {
	$@
	exit $?
}
optin() {
	OPT=$1
	shift
	OPTS=$@
	for i in $OPTS
	do
		[[ "$OPT" == "$i" ]] && return 0
	done
	return 1
}
gettime() {
	FILE=`readlink -f ./$1`
	if [ ! -f "$FILE" ]
	then
		echo 0
		return 1
	fi
	echo `stat -c%Y "$FILE"`
	return 0
}
TRUE=0
FALSE=1
OPTS=""
for i in $@
do
	OPTS="$OPTS $i"
done
[ -z "$OPTS" ] && OPTS="swig compile link"
COMPILER="gcc"
WRAPPERS="$MODNAME"_wrap.c
if [[ $BUILDLANG == "c++" ]]
then
	COMPILER="g++"
	WRAPPERS="$MODNAME"_wrap.cpp
fi
ALLSOURCES="$SOURCES $WRAPPERS"
OBJECTS=""
SOURCES=""
SWIGNEEDED=$FALSE
for i in $WRAPPERS
do
	if [ `gettime "$i"` -le `gettime "$INTERFACE"` ]
	then
		SWIGNEEDED=$TRUE
		break;
	fi
done
for i in $ALLSOURCES
do
	ans="`echo $i | sed 's:\(.*\)\..*:\1.o:g'`"
	OBJECTS="$OBJECTS $ans"
	[ -f "$i" ] && {
		if [ `gettime "$ans"` -le `gettime "$i"` ]
		then
			if (optin $i $WRAPPERS)
			then
				if [ $SWIGNEEDED -eq $FALSE ]
				then
					SOURCES="$SOURCES $i"
				fi
			else
				SOURCES="$SOURCES $i"
			fi
		fi
	}
done
if [ $SWIGNEEDED -eq $TRUE ]
then
	SOURCES="$SOURCES $WRAPPERS"
else
	for i in $WRAPPERS
	do
		if [ `gettime "$i"` -le `gettime "$INTERFACE"` ]
		then
			SOURCES="$SOURCES $i"
		fi
	done
fi
TEMP="$INCLUDES"
INCLUDES=""
for i in $TEMP
do
	INCLUDES="$INCLUDES -I$i"
done
TEMP="$LIBRARIES"
LIBRARIES=""
for i in $TEMP
do
	LIBRARIES="$LIBRARIES -l$i"
done
CLEAN="$OBJECTS $WRAPPERS"
[[ "$TYPE" == "python" ]] && CLEAN="$CLEAN $MODNAME.pyc"
if (optin clean $OPTS)
then
	echo "Cleaning workspace..."
	diec rm -rf $CLEAN
fi
[ $SWIGNEEDED -eq $TRUE ] && {
	if (optin swig $OPTS)
	then
		for i in $WRAPPERS
		do
			echo "[SWIG] Building $i from $INTERFACE"
			[[ $BUILDLANG == "c++" ]] && CPPBIT="-c++"
			SWIGCMD="swig -$TYPE $CPPBIT -o $i $INTERFACE"
			$SWIGCMD
			echo $SWIGCMD
			STATUS=$?
			if [ $STATUS -ne 0 ]
			then
				echo "[SWIG] Due to an error, building has been terminated"
				exit $FALSE
			fi
		done
	fi
}
if (optin compile $OPTS)
then
	for i in $SOURCES
	do
		DISPLANG="C"
		[[ $BUILDLANG == "c++" ]] && DISPLANG="C++"
		echo "[$DISPLANG] Building object $i"
		COMPILECMD="$COMPILER -c -fpic $i $INCLUDES $LIBRARIES"
		$COMPILECMD
		STATUS=$?
		if [ $STATUS -ne 0 ]
		then
			echo "[$DISPLANG] Due to an error, compiling has been terminated"
			exit $FALSE
		fi
	done
fi
if (optin link $OPTS)
then
		echo "[LINK] Linking $MODNAME"
		LINKCMD="$COMPILER -shared $OBJECTS -o _"$MODNAME".so"
		$LINKCMD
		STATUS=$?
		if [ $STATUS -ne 0 ]
		then
			echo "[LINK] Due to an error, linking has been terminated"
			exit $FALSE
		fi
fi

#EOF
