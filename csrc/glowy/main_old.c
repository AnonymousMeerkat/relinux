/*
 * main.cpp
 *
 * Main Glowy Source File
 *
 *  Created on: 2012-08-04
 *      Author: Anonymous Meerkat
 */

#include <python2.7/Python.h>

#define MODNAME "_glowy"

// Helper function
inline void createClass(const char* name, PyObject* moduleDict,
		PyObject* baseclasses, PyMethodDef* methods)
{
	PyMethodDef *def;
	PyObject *classDict = PyDict_New();
	PyObject *className = PyString_FromString(name);
	PyObject *theClass = PyClass_New(baseclasses, classDict, className);
	PyDict_SetItemString(moduleDict, name, theClass);
	Py_DECREF(classDict);
	Py_DECREF(className);
	Py_DECREF(theClass);
	// Add the methods
	for(def = methods; def->ml_name != NULL; def++)
	{
		PyObject *func = PyCFunction_New(def, NULL);
		PyObject *method = PyMethod_New(func, NULL, theClass);
		PyDict_SetItemString(classDict, def->ml_name, method);
		Py_DECREF(func);
		Py_DECREF(method);
	}
}

static PyObject* button_init(PyObject *self, PyObject *args)
{
	printf("hello\n");
	Py_INCREF(Py_None);
	return (Py_None);
}

static PyMethodDef ButtonMethods[] =
{
{ "__init__", button_init, METH_VARARGS, "test" }, };

static PyMethodDef ModuleMethods[] =
{
{ NULL }, };

PyMODINIT_FUNC init_glowy(void)
{
	PyImport_AddModule(MODNAME);
	PyObject *module = Py_InitModule(MODNAME, ModuleMethods);
	PyObject *moduleDict = PyModule_GetDict(module);
	PyImport_ImportModule("Tkinter");
	//Py_BuildValue("(s)", "Tkinter.Canvas")
	printf("hiiiii\n");
	PyObject* tuple =  PyTuple_Pack(1, Py_None);
	printf("yeah\n");
	createClass("Button", moduleDict, tuple, ButtonMethods);
	printf("hiii\n");
	createClass("Button2", moduleDict, NULL, ButtonMethods);
}

int main(int argc, char *argv[])
{
	Py_SetProgramName(argv[0]);
	Py_Initialize();
	init_glowy();
	Py_Exit(0);
	return (0);
}
