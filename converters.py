from pathlib import Path

from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np

def splitter_decorator(dtype: None = None, min_length: int = 1):
    """Split the input value and convert it to dtype
    """
    def decorator(funct):
        def wrapper(val, sep=' '):
            # Check
            if val is None:
                return val

            # Split value
            aux = funct(val, sep=sep)

            # Convert
            if dtype is not None:
                aux = list(map(dtype, aux))

            # Check length
            if min_length <= 0 and len(aux) == 1:
                aux = aux[0]
            elif len(aux) < min_length:
                raise ValueError('Value length smaller than accepted')

            return aux
        return wrapper
    return decorator 

def coma_splitter(val: str, sep: str = None) -> list:
    if ',' in val:
        aux = val.split(',')
    elif sep is None:
        aux = val.split()
    else:
        aux = val.split(sep)

    return aux

@splitter_decorator
def list_converter(val: str, sep: str = ' '):
    return val.split(sep)

@splitter_decorator(dtype=int)
def intlist_converter(val: str, sep: str = None):
    return coma_splitter(val, sep=sep)

@splitter_decorator(dtype=float)
def floatlist_converter(val: str, sep: str = None):
    return coma_splitter(val, sep=sep)

def path_converter(val):
    if val is None:
        return val
    else:
        aux = Path(val)
        return aux.expanduser()

def skycoord_converter(val):
    if val is None:
        return val
    else:
        ra, dec, frame = val.split()
        return SkyCoord(ra, dec, frame=frame)

def astropy_converter(val: str, dtype: str):
    """Convert to an astropy type

    Accepted dtypes: quantity, skycoord

    Parameters:
        val (str): input string
        dtype (type): convert to this type

    Returns:
        val (dtype): val converted to the type

    Raises:
        NotImplementedError: if dtype is not available
    """
    if dtype.lower()=='quantity':
        aux = val.split()
        if len(aux) < 2:
            return float(aux[0]) * u.dimensionless_unscaled
        elif len(aux) == 2:
            return float(aux[0]) * u.Unit(aux[1])
        else:
            return np.array(aux[:-1], dtype=float) * u.Unit(aux[-1])
    elif dtype.lower()=='skycoord':
        try:
            ra, dec, frame = val.split()
        except ValueError:
            ra, dec = val.split()
            frame = 'icrs'
        return SkyCoord(ra, dec, frame=frame)
    else:
        raise NotImplementedError('converter to %s not available' % dtype)
 

