"""An advanced version of the `ConfigParser` class."""
import configparser as cparser

import astropy.units as u
import numpy as np

from .converters import (astropy_converter, list_converter, intlist_converter,
                         floatlist_converter, path_converter,
                         skycoord_converter)

def get_boolean(value) -> bool:
    """Convert `value` to boolean as defined in `configparser`."""
    if value.strip().lower() in ['1', 'yes', 'true', 'on']:
        return True
    elif value.strip().lower() in ['0', 'no', 'false', 'off']:
        return False
    else:
        raise ValueError(f'Cannot convert to boolean: {value}')

class ConfigParserAdv(cparser.ConfigParser):
    """Extend the `configparser.ConfigParser` behaviour."""

    def __init__(self, **kwargs):
        converters = {
            'list': list_converter, 
            'intlist': intlist_converter,
            'floatlist': floatlist_converter, 
            'path': path_converter,
            'skycoord': skycoord_converter,
        }
        try:
            converters.update(kwargs.pop('converters'))
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
            if val[-1].strip() in ['dimless', 'dimensionless', 'nounit', '1']:
                unit = u.dimensionless_unscaled
            else:
                unit = u.Unit(val[-1])
            return np.array(val[:-1], dtype=float) * unit

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
            'fallback': None, 
            'n': None, 
            'sep': ' ', 
            'dtype': None,
            'allow_global': True,
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
        except AttributeError:
            pass

        # Convert
        if opts['dtype'] is None or value is None:
            return value
        else:
            try:
                if opts['dtype'] == bool:
                    return get_boolean(value)
                else:
                    return opts['dtype'](value)
            except TypeError:
                return astropy_converter(value, opts['dtype'])

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

