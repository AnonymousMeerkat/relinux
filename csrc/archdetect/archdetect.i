// Interface file for ArchDetect
// Used by SWIG
%module relinux_archdetect

%inline
%{
extern void getarch();
%}
