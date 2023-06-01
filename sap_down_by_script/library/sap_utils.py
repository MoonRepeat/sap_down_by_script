import os
import os.path
import shutil
import datetime
from threading import Thread
import functools
import pandas as pd

class SapUtils:
    def timeout(func):
        """A decorator that generates an error
        if the function runs longer than a certain amount of time.
            : To use, timeout_time must be defined
            : as an integer as a class property.
            : (After waiting for the corresponding integer seconds,
            : an error is generated if exceeded)
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timeout_time = args[0].timeout_time
            res = [Exception('function [%s] timeout [%s seconds] exceeded!'
                             % (func.__name__, timeout_time))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout_time)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    
    def make_file_path(file_path: str) -> None:
        """After checking whether the folder in file_path exists,
        create a folder if it does not exist,
        delete the existing file in that path

        Args:
            file_path (str) : File path
        Return:
            None
        """
        if (not os.path.isdir(file_path)):
            os.makedirs(file_path)
        else:
            __class__.delete_file(file_path=file_path, file_all=True)
        
        return None
    
    def delete_file(**kwargs) -> None:
        """Delete file

        **Kwargs:
            file_path (str): (default : ".\\") File path
            file_name (str): Name of the file to delete (including extension)
            file_extension (str): Extension of the file to be deleted.
            file_all (boolean): (default = False)
                If you enter True, all files in that path will be deleted.
        Return:
            None
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\', 'file_all': False}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # If extension is entered, all files with that extension are deleted.
        if 'file_extension' in kwargs.keys():
            file_list = os.listdir(kwargs['file_path'])
            for file_selected in file_list:
                if file_selected.endswith(kwargs['file_extension']):
                    try:
                        os.remove('{}{}'.format(kwargs['file_path'], 
                                                file_selected))
                    except:
                        pass
        # When a file name is entered, only that file is deleted
        if 'file_name' in kwargs.keys():
            try:
                os.remove('{}{}'.format(kwargs['file_path'], 
                                        kwargs['file_name']))
            except:
                pass
        # Delete all files if delete all files is True
        if kwargs['file_all']:
            file_list = os.listdir(kwargs['file_path'])
            for file_selected in file_list:
                try:
                    os.remove('{}{}'.format(kwargs['file_path'],
                                            file_selected))
                except:
                    pass
        
        return None

    def rename_file(file_name: str, new_file_name: str, **kwargs) -> None:
        """Rename file

        Args:
            file_name (str): File name
            new_file_name (str): New file name
        **Kwargs:
            file_path (str): (Default='.\\') file path
        Return:
            None
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # Rename file
        try:
            os.rename('{}{}'.format(kwargs['file_path'], file_name),
                      '{}{}'.format(kwargs['file_path'], new_file_name))
        except:
            pass
        
        return None
    
    def move_file(file_name: str, new_file_path: str, **kwargs) -> None:
        """Move file
    
        Args:
            file_name (str) : file name
            new_file_path (str): File path to move
        **Kwargs:
            file_path : (Default='.\\') file path
        Return:
            None
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # Move file
        try:
            shutil.move('{}{}'.format(kwargs['file_path'], file_name),
                        '{}{}'.format(new_file_path, file_name))
        except:
            pass
        
        return None

    def make_str_date(days: int, **kwargs) -> str:
        """Receives an integer and returns the date
        moved by the input date based on today

        Args:
            days (int): Enter the date to move from today's date as an integer

        **Kwargs:
            type (str): Type to return date (default: %Y.%m.%d)

        Returns:
            str: Return date as str
        """
        # Setting the default value of kwargs
        default_kwargs = {'type': '%Y.%m.%d'}
        kwargs = { **default_kwargs, **kwargs }
    
        str_date = (datetime.datetime.today() + datetime.timedelta(days)).\
            strftime(kwargs['type'])
        
        return str_date
    
    def get_file_size(file_name: str, **kwargs) -> int:
        """Check file size

        Args:
            file_name (str): File name (including extension)

        **Kwargs:
            file_path (str)(default='.\\'): File path

        Returns:
            int: File size
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        file_size = os.path.getsize(os.path.join(kwargs['file_path'],
                                                 file_name))
        
        return file_size
    
    def chk_file_exist(file_name: str, **kwargs) -> bool:
        """Check if the file exists

        Args:
            file_name (ste): File name

        **Kwargs:
            file_path (str)(default='.\\'): File path

        Returns:
            bool: Return True if the file exists
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        checker = os.path.isfile(os.path.join(kwargs['file_path'], file_name))
        
        return checker
    
    def read_xlsx_to_dataframe(file_name: str, **kwargs) -> pd.DataFrame:
        """Read excel file and return it as pd.DataFrame

        Args:
            file_name (str): File name (including extension)
            
        **kwargs
            file_path (str): (Default='.\\') file path

        Returns:
            pd.DataFrame: Contents of excel file in the form of a DataFrame
        """
        # Setting the default value of kwargs
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        file_name = os.path.join(kwargs['file_path'], file_name)
        df = pd.read_excel(file_name)
        
        return df