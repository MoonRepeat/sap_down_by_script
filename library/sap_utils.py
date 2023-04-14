import os
import os.path
import shutil
import datetime
from threading import Thread
import functools
import pandas as pd

class SapUtils:
    def timeout(func):
        """함수가 일정 시간 이상 작동하면 에러를 생성시키는 데코레이터
            : 사용을 위해서는 Class 속성으로 timeout_time이 정수 형태로 정의 되어 있어야 함
            : (해당 정수 초만큼 대기 후 초과시 에러 생성)
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timeout_time = args[0].timeout_time
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout_time))]
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
        """file_path의 폴더가 있는지 확인 후 없으면 폴더 생성 폴더가 있을 경우 해당 경로 기존 파일 삭제

        Args:
            file_path (str) : 폴더 전체 경로
        Return:
            None
        """
        # 폴더 있는지 확인 후 없으면 생성
        if (not os.path.isdir(file_path)):
            os.makedirs(file_path)
        
        return None
    
    def delete_file(**kwargs) -> None:
        """입력 받은 파일 삭제

        **Kwargs:
            file_path (str)(default : ".\\"): 파일 경로
            file_name (str): 삭제할 파일의 이름(확장자 포함)
            file_extension (str): 삭제할 파일의 확장자. 해당 확장자 파일 일괄 삭제
            file_all (boolean)(default = False): True 입력 할 경우 해당 경로의 모든 파일 삭제
        Return:
            None
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\', 'file_all': False}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # 파일 확장자를 입력 받으면 해당 확장자 파일 모두 삭제
        if 'file_extension' in kwargs.keys():
            file_list = os.listdir(kwargs['file_path'])
            for file_selected in file_list:
                if file_selected.endswith(kwargs['file_extension']):
                    try:
                        os.remove('{}{}'.format(kwargs['file_path'], file_selected))
                    except:
                        pass
        # 파일 이름을 입력 받으면 해당 파일 만 삭제
        if 'file_name' in kwargs.keys():
            try:
                os.remove('{}{}'.format(kwargs['file_path'], kwargs['file_name']))
            except:
                pass
        # 파일 전체 삭제가 True 일 경우 모든 파일 삭제
        if kwargs['file_all']:
            file_list = os.listdir(kwargs['file_path'])
            for file_selected in file_list:
                try:
                    os.remove('{}{}'.format(kwargs['file_path'], file_selected))
                except:
                    pass
        
        return None

    def rename_file(file_name: str, new_file_name: str, **kwargs) -> None:
        """파일 이름 변경

        Args:
            file_name (str): 기존 파일 이름
            new_file_name (str): 변경할 파일 이름
        **Kwargs:
            file_path (str): 파일 경로
        Return:
            None
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # 파일 이름 변경
        try:
            os.rename('{}{}'.format(kwargs['file_path'], file_name),
                      '{}{}'.format(kwargs['file_path'], new_file_name))
        except:
            pass
        
        return None
    
    def move_file(file_name: str, new_file_path: str, **kwargs) -> None:
        """지정된 파일 이동 함수(파일명 변경 포함)
    
        Args:
            file_name (str) : 파일 이름
            new_file_path (str): 이동할 파일 경로
        **Kwargs:
            file_path : 원래 파일 경로
        Return:
            None
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # 파일 이동
        try:
            shutil.move('{}{}'.format(kwargs['file_path'], file_name),
                        '{}{}'.format(new_file_path, file_name))
        except:
            pass
        
        return None

    def make_str_date(days: int, **kwargs) -> str:
        """일자를 정수로 입력 받아 오늘 기준으로 입력 받은 날짜 만큼 이동한 일자를 반환

        Args:
            days (int): 오늘 일자를 기준으로 이동할 일자를 정수로 입력

        **Kwargs:
            type (str): 날자를 반환할 타입 (default: %Y.%m.%d)

        Returns:
            str: 날짜를 문자 형태로 반환
        """
        
        default_kwargs = {'type': '%Y.%m.%d'}
        kwargs = { **default_kwargs, **kwargs }
    
        str_date = (datetime.datetime.today() + datetime.timedelta(days)).strftime(kwargs['type'])
        
        return str_date
    
    def get_file_size(file_name: str, **kwargs) -> int:
        """입력 받은 파일 용량 확인 하여 반환

        Args:
            file_name (str): 파일 이름(확장자 포함)

        **Kwargs:
            file_path (str)(default='.\\'): 파일 경로

        Returns:
            int: 파일 용량
        """
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        file_size = os.path.getsize(os.path.join(kwargs['file_path'], file_name))
        
        return file_size
    
    def chk_file_exist(file_name: str, **kwargs) -> bool:
        """해당 되는 파일이 있는지 여부를 확인

        Args:
            file_name (ste): 파일 이름

        **Kwargs:
            file_path (str)(default='.\\'): 파일 경로

        Returns:
            bool: 있으면 True
        """
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        checker = os.path.isfile(os.path.join(kwargs['file_path'], file_name))
        
        return checker
    
    def read_xlsx_to_dataframe(file_name: str, **kwargs) -> pd.DataFrame:
        """지정된 엑셀 파일을 읽어서 pd.DataFrame 형태로 반환

        Args:
            file_name (str): 파일 이름(확장자 포함)
            
        **kwargs
            file_path (str): (Default='.\\') 파일 저장된 경로

        Returns:
            pd.DataFrame: 엑셀 파일의 내용을 DataFrame 형태로 반환
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        
        file_name = os.path.join(kwargs['file_path'], file_name)
        df = pd.read_excel(file_name)
        
        return df