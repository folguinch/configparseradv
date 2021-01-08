from typing import List
import configparser as cparser
import os

import astropy.units as u
import numpy as np

import configparseradv.converters as conv

class ConfigParserAdv(cparser.ConfigParser):
    """Extend the configparser.ConfigParser behaviour.
    """

    def __init__(self, **kwargs):
        converters = {
            'list':conv.list_converter, 
            'intlist':conv.intlist_converter,
            'floatlist':conv.floatlist_converter, 
            'path':conv.path_converter,
            'skycoord':conv.skycoord_converter,
        }
        try:
            converters = converters.update(kwargs.pop('converters'))
        except KeyError:
            pass
        interpolation = kwargs.pop('interpolation', 
                                   cparser.ExtendedInterpolation())
        super().__init__(converters=converters, 
                         interpolation=interpolation, 
                         **kwargs)

    def getquantity(self, *args, **kwargs):
        """Return an ``astropy.Quantity`` from the parser data.

        Input parameters are the same as for ``parser.get(*args,**kwargs)``.
        """
        val = self.get(*args, **kwargs)

        # If the value was changed then it may be already a quantity
        if hasattr(val, 'unit'):
            return val
        else:
            # Or it may be a dimensionless float or float array
            try:
                # Set dimenssionless unit
                return (val + 0) * u.Unit(1)
            except TypeError:
                pass
        
        # Fallback values
        if val is None or len(val) == 0:
            return val
        else:
            val = val.split()

        # Convert string to quantity
        if len(val) == 1:
            # Dimesionless
            return float(val[0]) * u.Unit(1)
        elif len(val) == 2:
            # Single quantity
            return float(val[0]) * u.Unit(val[1])
        else:
            # Array of values
            try:
                # Check if dimensionless
                aux = float(val[-1])
                return np.array(val, dtype=float) * u.Unit(1)
            except ValueError:
                return np.array(val[:-1], dtype=float) * u.Unit(val[-1])

    def getvalue(self, *args, **kwargs):
        """Get values and convert if needed.
        
        Args:
          fallback: optional; default value.
          n: optional; if several values return value n.
          sep: optional; separator between values.
          dtype: optional; type for conversion. 
            Astropy objects available: quantity, skycoord.
          allow_global: optional; if one value is given but n!=0 use this value
            as default.
        """
        # Options
        opts = {
            'fallback':None, 
            'n':None, 
            'sep':' ', 
            'dtype':None,
            'allow_global':True,
        }
        opts.update(kwargs)
        
        # Abbreviations
        n = int(opts['n'])
        key = args[1]
        getkw = {'fallback':opts['fallback']}

        # Get values
        subkey = f'{key}{n}'
        if n is not None and subkey in self.options(args[0]):
            value = self.get(args[0], subkey, **getkw)
        elif key in self.options(args[0]):
            value = self.get(*args, **getkw)
            if n is not None:
                value = value.split(opts['sep'])
                if len(value) == 1:
                    if n != 0 and not opts['allow_global']:
                        value = opts['fallback']
                    else:
                        value = value[0]
                else:
                    try:
                        value = value[n]
                    except IndexError:
                        print(f'WARNING: {key} not in values list,' + \
                              ' using fallback')
                        value = opts['fallback']
        else:
            value = opts['fallback']
        
        # Strip spaces
        try:
            value = value.strip()
        except:
            pass

        # Convert
        if opts['dtype'] is None or value is None:
            return value
        else:
            try:
                return opts['dtype'](value)
            except TypeError:
                return astropy_converter(value, opts['dtype'])

    def getkeys(self, section: str, keys: List[str], 
            fallbacks: list = [None]) ->  list:
        """Return the values in list of keys.
        
        Args:
          section: configuration file section.
          keys: section options to read.
          fallbacks: optional; fallback values.
        """
        if len(fallbacks) == 1 and len(keys) != 1:
            fallbacks = fallbacks * len(keys)
        elif len(fallbacks) != len(keys):
            raise ValueError('Fallbacks and keys lengths do not match')
        else:
            pass

        return [self.get(section, key, fallback=fall) for key, fall in zip(keys, fallbacks)]

    def getfloatkeys(self, section: str, keys: List[str], 
            fallbacks: List[float] = ['nan']) -> list:
        """Return the values in list of keys converted to float.
        
        Args:
          section: configuration file section.
          keys: section options to read.
          fallbacks: optional; fallback values.
        """
        return list(map(float,
                        self.getkeys(section, keys, fallbacks=fallbacks)))

    def getintkeys(self, section: str, keys: List[str], 
            fallbacks: List[int] = ['nan']) -> list:
        """Return the values in list of keys converted to int.
        
        Args:
          section: configuration file section.
          keys: section options to read.
          fallbacks: optional; fallback values.
        """
        return list(map(int,
                        self.getkeys(section, keys, fallbacks=fallbacks)))

    def getboolkeys(self, section: str, keys: List[str], 
            fallbacks: List[bool] = [False]) -> list:
        """Return the values in list of keys converted to boolean.
        
        Args:
          section: configuration file section.
          keys: section options to read.
          fallbacks: optional; fallback values.
        """
        if len(fallbacks) == 1 and len(keys) != 1:
            fallbacks = fallbacks * len(keys)
        elif len(fallbacks) != len(keys):
            raise ValueError('Fallbacks and keys lengths do not match')
        else:
            pass

        return [self.getboolean(section, key, fallback=fall) for key, fall in zip(keys, fallbacks)]

    def getvalueiter(self, *args, **kwargs):
        """Iterator over velues in option.
        
        Args:
          sep: optional; value separator.
        """
        opts = {'sep':kwargs.get('sep', ' '), 'n':0, 'allow_global':False}
        while self.getvalue(*args, **opts):
            kwargs['n'] = opts['n']
            value = self.getvalue(*args, **kwargs)
            if value is not None:
                yield value
            else:
                break
            opts['n'] = opts['n'] + 1

