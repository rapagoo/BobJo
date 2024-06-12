#include <Python.h>

// Function to count the number of stations
static PyObject* count_stations(PyObject* self, PyObject* args) {
    PyObject* list;
    int count;

    if (!PyArg_ParseTuple(args, "O", &list))
        return NULL;

    count = PyList_Size(list);

    return Py_BuildValue("i", count);
}

// Method definitions
static PyMethodDef SpamMethods[] = {
    {"count_stations", count_stations, METH_VARARGS, "Count the number of stations."},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",
    "It is a test module.",
    -1,
    SpamMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_spam(void) {
    return PyModule_Create(&spammodule);
}
