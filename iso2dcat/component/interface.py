"""Interfaces for the components"""

from zope import interface


class IDBFunc(interface.Interface):
    """
    Marker Interface for DBFunc utility
    """

class IIsoCfg(interface.Interface):
    """
    Marker Interface for Config utility
    Special Interface to mark given config or loaded default config
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
    Marker interface for all entities
    """


class ICatalog(IEntity):
    """
    Marker interface for Catalog entities
    """
    pass


class IRDFDatabase(interface.Interface):
    """
    Marker interface for RDF Database
    """

class INamespaceManager(interface.Interface):
    """
    Marker interface for NamespaceManager
    """

class ILanguageMapper(interface.Interface):
    """
    Marker Interface for global Language Mapping
    """
