"""Utilities for working with `ConfigParserAdv` objects"""
from typing import List, Sequence, Optional, Union

Parser = Union['configparseradv.configparser.ConfigParserAdv',
               'configparser.SectionProxy']

def get_keys(config: Parser, keys: List[str], section: Optional[str] = None,
             fallbacks: Sequence = (None,)) ->  List:
    """Return the values in list of keys.
    
    Args:
      config: config parser or parser proxy.
      keys: section options to read.
      section: optional; configuration file section (if not a proxy).
      fallbacks: optional; fallback values.
    """
    if len(fallbacks) == 1 and len(keys) != 1:
        fallbacks = fallbacks * len(keys)
    elif len(fallbacks) != len(keys):
        raise ValueError('Fallbacks and keys lengths do not match')
    else:
        pass

    values = []
    for key, fallback in zip(keys, fallbacks):
        if section is None:
            values.append(config.get(key, fallback=fallback))
        else:
            values.append(config.get(section, key, fallback=fallback))

    return values

def get_floatkeys(config: Parser, keys: List[str],
                  section: Optional[str] = None,
                  fallbacks: Sequence[float] = ('nan',)) -> List:
    """Return the values in list of keys converted to float.
    
    Args:
      config: config parser or parser proxy.
      keys: section options to read.
      section: optional; configuration file section.
      fallbacks: optional; fallback values.
    """
    return list(map(float, get_keys(config, keys, section=section,
                                    fallbacks=fallbacks)))

def get_intkeys(config: Parser, keys: List[str], section: Optional[str] = None,
                fallbacks: Sequence[int] = ('nan',)) -> List:
    """Return the values in list of keys converted to int.
    
    Args:
      config: config parser or parser proxy.
      keys: section options to read.
      section: optional; configuration file section.
      fallbacks: optional; fallback values.
    """
    return list(map(int, get_keys(config, keys, section=section,
                                  fallbacks=fallbacks)))

def get_boolkeys(config: Parser, keys: List[str],
                 section: Optional[str] = None,
                 fallbacks: Sequence[bool] = (False,)) -> List:
    """Return the values in list of keys converted to boolean.
    
    Args:
      config: config parser or parser proxy.
      keys: section options to read.
      section: optional; configuration file section.
      fallbacks: optional; fallback values.
    """
    if len(fallbacks) == 1 and len(keys) != 1:
        fallbacks = fallbacks * len(keys)
    elif len(fallbacks) != len(keys):
        raise ValueError('Fallbacks and keys lengths do not match')
    else:
        pass

    values = []
    for key, fallback in zip(keys, fallbacks):
        if section is None:
            values.append(config.getboolean(key, fallback=fallback))
        else:
            values.append(config.getboolean(section, key, fallback=fallback))
    return values
