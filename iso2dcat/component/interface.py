"""Interfaces for the components"""

from zope import interface


class ICfg(interface.Interface):
    """
    Marker Interface for Config utility
    """


class IDBFunc(interface.Interface):
    """
    Marker Interface for DBFunc utility
    """


class ILogger(interface.Interface):
    """
    Marker Interface for logger utility
    """


class IDataStorage(interface.Interface):
    """
    Marker Interface for global data storage
    """


class IParams(interface.Interface):
    """
    Marker Interface for global params
    """


class IDBConstructor(interface.Interface):
    """
    Marker Interface for global test DB creator
    """


class IDCM(interface.Interface):
    """
    Marker Interface for global Dataset catalog mapping
    """


class IStat(interface.Interface):
    """
    Statistical information
    """


class IEntity(interface.Interface):
    """
    MArker interface fpr all entities
    """


class ICatalog(IEntity):
    pass



class IRDFDatabase(interface.Interface):
    """
    Marker interface for RDF Database
    """
