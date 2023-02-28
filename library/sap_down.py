import os
import os.path
import re
import time
import pandas as pd
import random
from tqdm import tqdm
from itertools import product
from library import sap_utils


class SapDown:
    __sap_setting = dict()
    
    def __init__(self, name: str, script_setting: dict, **kwargs):
        """객체의 속성 인자 정의 및 초기화:
        
        속성 인자:
            __script_setting (dict): 해당 SAP Script를 작동하기 위한 설정
            __sap_my_df (DataFrame): 필요시 다른 객체가 사용 할 수 있게 다운 받은 정보를 별도 저장하는 공간
            __sap_reference_df (DataFrame) : 파일 다운에 필요한 참고용 데이터를 다운 객체에서 받아서 보관 하는 공간

        Args:
            name (str): 해당 SAP Script의 이름
            script_setting (dict): 해당 SAP Script를 작동하기 위한 설정
            
        Return:
            void
        """
        self.__my_name = name
        self.__script_setting = script_setting.copy()
        self.timeout_time = script_setting['time_out']
        
        if 'sap_setting' in kwargs:
            SapDown.__sap_setting = kwargs['sap_setting']
        
        if 'make_data' in script_setting:
            if script_setting['make_data']:
                self.__sap_my_df = pd.DataFrame(columns=script_setting['data_col_rename_list'])
        if 'reference_data' in script_setting:
            if script_setting['reference_data'] != None:
                self.__sap_reference_df = pd.DataFrame()

    def set_reference_df(self, reference_df: pd.DataFrame) -> None:
        """SAP Script를 실행하기 위한 참고용 정보를 저장

        Args:
            reference_df (DataFrame): SAP Script를 싱행하기 위한 참고용 데이터
            
        Return:
            None
        """
        self.__sap_reference_df = reference_df.copy()
    
    def get_my_df(self) -> pd.DataFrame:
        """현재 객체가 보유한 데이터를 반환

        Returns:
            pd.DataFrame: SAP Script 실행 중 얻게된 데이터 반환
        """
        return self.__sap_my_df

    def start_sap_client(self) -> None:
        """SAP Client를 실행
        
        Return:
            None
        """
        # SAP Client 실행을 위한 Command를 str로 생성
        sap_run_batch = '{0}sapshcut -system={1} -client={2}'.format(
            SapDown.__sap_setting['sap_program_path'], 
            SapDown.__sap_setting['sap_system'], 
            SapDown.__sap_setting['sap_client'])
        if not SapDown.__sap_setting['auto_login']:
            sap_run_batch = "{0} -user={1} -pw={2}".format(
                sap_run_batch, 
                SapDown.__sap_setting['user_id'], 
                SapDown.__sap_setting['user_pass'])
        
        # SAP Client 실행 및 실행 될 때 까지 일정 시간 대기(60초)
        os.system(sap_run_batch)
        time.sleep(60)

    def end_sap_client(self) -> None:
        """SAP Client 종료 및 Windows Visual Basic Script 종료(Taskkill 사용)

        Return:
            None
        """
        # SAP Client 종료 하기 위한 Command를 실행
        sap_run_batch1 = '{} {} {}'.format('taskkill /f /im', 
                                           SapDown.__sap_setting['sap_program_file'],
                                           '> null 2>&1'
                                           )
        sap_run_batch2 = 'taskkill /f /im wscript.exe > null 2>&1'
        
        # SAP Client 종료 및 종료 될 때 까지 일정 시간 대기(10초)
        os.popen(sap_run_batch1)
        time.sleep(10)
        os.popen(sap_run_batch2)
        time.sleep(10)

    def restart_sap_client(self) -> None:
        """SAP Client 재시작

        Return:
            None
        """
        # SAP Client 종료 --> 실행
        self.end_sap_client()
        self.start_sap_client()
    
    def down_file_sap(self) -> None:
        """SAP에서 파일 받는 VBS를 돌리는 시작 함수

        Returns:
            list: 생성한 파일들의 이름 list
        """
        fun_switch = {'@txt': self.__down_txt_from_sap,
                      '@txt_xlsx': self.__down_txt_to_xlsx_from_sap,
                      '@pdf': self.__down_pdf_from_sap
                      }
        file_name_list = fun_switch[self.__script_setting['run_type']]()
        
        return file_name_list

    def __query_reference_df(self, input_code_list: list) -> pd.DataFrame:
        """SAP에 입력할 값을 받아서 해당 값을 Query 기준으로 잡아 __sap_my_df에서 검색하여 행을 반환
        !!!!!!! 무식하게 프로그램 하였음 - 수정 필요!!!!!!

        Args:
            input_code_list (list): SAP에 입력되는 Input code 리스트

        Returns:
            pd.DataFrame: Query 결과에 대한 DataFarme
        """
        rf_code_dict = dict()
        
        for i, input_code in enumerate(input_code_list, start=1):
            if self.__script_setting['input_code' + str(i)][0][0] == '@':
                rf_code_dict[self.__script_setting['input_code' + str(i)][0][1:]] = input_code
                
        
        result_df = self.__sap_reference_df.copy()
        
        for query_key in rf_code_dict:
            result_df = result_df[result_df[query_key] == rf_code_dict[query_key]]
        
        return result_df

    def __make_file_name(self, input_code_list: list, **kwargs) -> str:
        """SAP Query에 사용할 code에 대한 list를 받아 Script Setting의 File Name 룰과 같이 확인 하여 파일 이름을 반환

        Args:
            input_code_list (list): 현재 SAP에 입력할 code 값에 대한 list
        
        **Kwargs:
            extension (str)(default=''): 확장자 까지 포함된 파일이름 반환 원할 경우 사용

        Returns:
            str: 파일 이름
        """
        default_kwargs = {'extension': ''}
        kwargs = { **default_kwargs, **kwargs }
        file_name = sap_utils.SapUtils.make_str_date(0, type='%y%m%d')        
        file_name_rule_list = self.__script_setting['file_name']
        reference_df = pd.DataFrame()
        
        if self.__script_setting['reference_data'] != None:
            reference_df = self.__query_reference_df(input_code_list)
                
        for file_name_rule in file_name_rule_list:
            if file_name_rule[0] == '@':
                if file_name_rule[:11] == '@input_code':
                    list_index_no = int(file_name_rule[-1]) - 1
                    file_name_temp = input_code_list[list_index_no]
                else:
                    file_name_temp = reference_df.loc[:, file_name_rule[1:]].tolist()[0]
            else:
                file_name_temp = file_name_temp
            
            file_name = '{}-{}'.format(file_name, file_name_temp)
        
        if len(kwargs['extension']) > 0:
            file_name = '{}.{}'.format(file_name, kwargs['extension'])
        
        return file_name

    def __make_iterate_list(self) -> list:
        """SAP Script를 실행 할 때 반복 입력하는 값을 리스트 형태로 반환
        !!!!!!! 무식하게 프로그램 하였음 - 수정 필요!!!!!!

        Returns:
            list: 2차원 형태의 리스트
        """
        iterate_list = list()
        iterate_key = self.__script_setting['iterate_key']
        temp_iterate_list = list()
        new_iterate_list = list()
        
        # interate key가 파일 명일 경우 전 처리
        if iterate_key[0] == '@':
            file_name = iterate_key[1:]
            file_path = self.__script_setting['sap_script_path']
            file_df = sap_utils.SapUtils.read_xlsx_to_dataframe(file_name, file_path=file_path)
            
            iterate_key = str()
            for i in range(1, len(file_df.columns) + 1):
                iterate_key = iterate_key + i
                if i != len(file_df.columns):
                    iterate_key = iterate_key + '&'
                
                self.script_setting['{}{}'.format('input_code', i)] = file_df.iloc[:, 3].to_list()
            
        iterate_key_list = re.findall(r'\d+|\W', iterate_key)
        iterate_key_no_list = re.findall(r'\d+', iterate_key)
        
        # iterate key의 숫자 부분 확인하여 그 숫자 갯수 만큼 input_code? 형태의 변수 생성
        for i in iterate_key_no_list:
            locals()['{}{}'.format('input_code', i)] = self.__script_setting['{}{}'.format('input_code', i)]
            if locals()['{}{}'.format('input_code', i)][0][0] == '@':
                locals()['{}{}'.format('input_code', i)] = self.__sap_reference_df[locals()['{}{}'.format('input_code', i)][0][1:]].tolist()
            
            for j in range(len(locals()['{}{}'.format('input_code', i)])):
                locals()['{}{}'.format('input_code', i)][j] = [locals()['{}{}'.format('input_code', i)][j]]
        
        # & 형태는 모두 합치고 | 형태만 남도록 변경
        i = 0
        iterate_key_list_copy = iterate_key_list.copy()
        while i != len(iterate_key_list_copy):
            if iterate_key_list_copy[i] == '&':
                for j in range(len(locals()['{}{}'.format('input_code', iterate_key_list_copy[i - 1])])):
                    locals()['{}{}'.format('input_code', iterate_key_list_copy[i - 1])][j].extend(locals()['{}{}'.format('input_code', iterate_key_list_copy[i + 1])][j])
                del iterate_key_list_copy[i:i + 2]
            else:
                i = i + 1
        
        # 새로운 숫자로만 구성된 키 리스트 생성
        iterate_key_no_list_copy = iterate_key_list_copy.copy()
        while '|' in iterate_key_no_list_copy:
            iterate_key_no_list_copy.remove('|')
        
        # 신규 리스트 생성
        for code in iterate_key_no_list_copy:
            new_iterate_list.append(locals()['{}{}'.format('input_code', code)])

        # 신규 리스트의 조합을 튜플로 생성 및 리스트로 변환
        for code in product(*new_iterate_list):
            temp_iterate_list.append([*code])
        for code_row in temp_iterate_list:
            temp_list = list()
            for code in code_row:
                temp_list.extend(code)
            iterate_list.append(temp_list)

        return iterate_list

    def __get_sap_cmd(self, file_name: str, input_code_list: list) -> str:
        """SAP Script 실행을 위한 명령어 생성 반환

        Args:
            file_name (str): Script 실행한 결과를 저장 할 파일 이름
            input_code_list (list): input_code1, 2, 3를 합한 list

        Returns:
            str: SAP Script 실행을 위한 구문
        """
        # SAP T-Code 앞에 처음으로 돌아가는 '/n' 문구 추가
        sap_t_code = self.__script_setting['sap_t_code']
        if sap_t_code[:2] != '/n':
            sap_t_code = '{}{}'.format('/n', sap_t_code)
        
        # SAP Script 실행 명령어
        run_sap_cmd = '{0}{1}.vbs'.format(
            SapDown.__sap_setting['sap_script_path'],
            self.__my_name
        )
        
        # SAP Script Args 입력
        run_sap_cmd = run_sap_cmd + ' ' + '{arg0} {arg1} {arg2} {arg3} {arg4} {arg5} {arg6}'.format(
            arg0=sap_t_code,
            arg1=self.__script_setting['plant_code'],
            arg2=sap_utils.SapUtils.make_str_date(self.__script_setting['start_date'], 
                                                  type=SapDown.__sap_setting['date_input_type']
                                                  ),
            arg3=sap_utils.SapUtils.make_str_date(self.__script_setting['end_date'],
                                                  type=SapDown.__sap_setting['date_input_type']
                                                  ),
            arg4=SapDown.__sap_setting['tempfile_save_path'],
            arg5=file_name,
            arg6=self.__script_setting['file_encoding']
        )
        
        # SAP Script Args 중 Input_code 입력
        for input_code in input_code_list:
            run_sap_cmd = '{} {}'.format(run_sap_cmd, input_code)
        
        return  run_sap_cmd

    def __down_txt_from_sap(self) -> list:
        """SAP에서 txt 형태의 파일을 다운 받는다. 다운 받은 파일 기반으로 sap_my_df 도 업데이트 한다.

        Returns:
            list: 다운 받은 파일명 리스트 반환
        """
        iterate_list = self.__make_iterate_list()
        file_name_list = list()
        
        sap_utils.SapUtils.delete_file(file_path=SapDown.__sap_setting['tempfile_save_path'], file_extension='txt')
        
        for input_code_list in tqdm(iterate_list):
            file_name = self.__make_file_name(input_code_list, extension='txt')
            run_sap_cmd = self.__get_sap_cmd(file_name, input_code_list)
            
            try:
                self.__run_sap_script(run_sap_cmd)
                
                if not sap_utils.SapUtils.chk_file_exist(file_name, file_path=SapDown.__sap_setting['tempfile_save_path']):
                    file_name = file_name.replace('.txt','-error.txt')
                    with open('{}{}'.format(SapDown.__sap_setting['tempfile_save_path'], file_name), 'w'):
                        pass
            except:
                file_name = file_name.replace('.txt','-timeout.txt')
                with open('{}{}'.format(SapDown.__sap_setting['tempfile_save_path'], file_name), 'w'):
                    pass
                self.restart_sap_client()
            else:
                self.__remove_txt_rows_cols(file_name)
                if self.__script_setting['make_data']:
                    if sap_utils.SapUtils.get_file_size(file_name, file_path=SapDown.__sap_setting['tempfile_save_path']) != 0:
                        temp_df = self.__change_txt_to_dataframe(file_name, file_path=SapDown.__sap_setting['tempfile_save_path'])[self.__script_setting['data_col_list']]
                        temp_df.columns = self.__script_setting['data_col_rename_list']
                        temp_df = temp_df.applymap(str)
                        for col_name in self.__script_setting['data_col_rename_list']:
                            temp_df[col_name] = temp_df[col_name].str.replace(pat=r'[^\w]', repl=r'', regex=True)
                        self.__sap_my_df = pd.concat([self.__sap_my_df, temp_df])
            
            file_name_list.append(file_name)
        
        return file_name_list
    
    def __down_txt_to_xlsx_from_sap(self) -> list:
        """SAP에서 txt 파일 다운 받아서 slsx 파일로 변환

        Returns:
            list: 파일 이름 list
        """
        file_name_list = self.__down_txt_from_sap()
        new_file_name_list = list()
        
        for file_name in file_name_list:
            df = self.__change_txt_to_dataframe(file_name, file_path=SapDown.__sap_setting['tempfile_save_path'])
            new_file_name = file_name.replace('.txt', '.xlsx')
            self.__change_dataframe_to_xlsx(df, new_file_name, file_path=SapDown.__sap_setting['tempfile_save_path'])
            new_file_name_list.append(new_file_name)
        
        return new_file_name_list
    
    # 미완성 만들어야 함.
    def __down_pdf_from_sap(self):
        pass
    
    # SAP Script 실행 중 시간이 오래 걸리면 Timeout error 발생
    @sap_utils.SapUtils.timeout
    def __run_sap_script(self, run_sap_cmd: str) -> None:
        """입력 받은 문자열을 Cmd 라인에서 실행

        Args:
            run_sap_cmd (str): cmd에서 실행할 문자열
            
        Return:
            None
        """
        os.system(run_sap_cmd)
        time.sleep(10)
    
    def __remove_txt_rows_cols(self, file_name: str, **kwargs) -> None:
        """txt 파일명을 입력 받아 입력된 행과 열 삭제 후 저장
        
        Args:
            file_name (str): 파일 이름 확장자 포함

        **Kwargs:
            file_path (str)(default = __sap_setting의 'tempfile_save_path): 파일 경로
            rows (list)(default = script_setting의 'del_row_no'): 삭제해야 할 행 리스트
            cols (list)(default = script_setting의 'del_col_no'):삭제해야 할 열 리스트

        Return:
            None
        """
        # kwargs의 default value 설정
        default_kwargs = {
            'file_path': SapDown.__sap_setting['tempfile_save_path'],
            'rows': self.__script_setting['del_row_no'], 
            'cols': self.__script_setting['del_col_no']}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')

        # 행열 삭제한 내용을 반영할 파일이름 생성
        new_file_name = '{0}{1}'.format(str(random.randrange(1000000, 9999999)), file_name)

        # 기존 파일의 내용을 읽어서 삭제 대상 행열을 건너띄며 신규 파일 작성
        with open('{0}{1}'.format(kwargs['file_path'], file_name), "r", encoding="UTF8") as rf,\
             open('{0}{1}'.format(kwargs['file_path'], new_file_name), "w", encoding="UTF8") as wf:
            i = 1
            while True:
                open_file_line = rf.readline()
                if not open_file_line:
                    break
                if i not in kwargs['rows']:
                    j = 1
                    for char in open_file_line:
                        if j not in kwargs['cols']:
                            wf.write(char)
                        if char == '\t':
                            j = j + 1
                i = i + 1
        
        # 기존 파일 삭제
        sap_utils.SapUtils.delete_file(file_path=kwargs['file_path'], file_name=file_name)
        # 신규 파일의 이름을 기존 파일 이름으로 변경
        sap_utils.SapUtils.rename_file(new_file_name, file_name, file_path=kwargs['file_path'])
    
    def __change_txt_to_dataframe(self, file_name: str, **kwargs) -> pd.DataFrame:
        """txt 파일을 입력 받아 DataFarme으로 변환

        Args:
            file_name (str): 파일 이름
        
        **Kwargs:
            file_path (str): 파일 경로
        
        Return:
            pd.DataFrame: txt의 읽은 값을 DataFrame으로 변환 하여 반환
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')
        
        # txt 파일 용량이 0보타 크면 내용을 읽어 DataFrame으로 변환하여 반환
        if os.path.getsize('{}{}'.format(kwargs['file_path'], file_name)) > 0:
            result = pd.read_table('{}{}'.format(kwargs['file_path'], file_name))
        else:
            result = pd.DataFrame()
        return result
    
    def __change_dataframe_to_xlsx(self, data_frame, file_name: str, **kwargs) -> bool:
        """DataFrame을 입력 받아 xlsx 파일로 변경하여 저장
    
        Args:
            data_frame (DataFrame): 변경 할 DataFrame
            file_name : 저장 할 파일 이름 (확장자 포함)
        
        **Kwargs:
            file_path (str)(default = '.\\'): 저장 할 파일의 경로
        
        Return
            bool: 생성 성공 여부
        """
        # kwargs의 default value 설정
        default_kwargs = {'file_path': '.\\'}
        kwargs = {**default_kwargs, **kwargs}
        if kwargs['file_path'][-1] != '\\':
            kwargs['file_path'] = '{}{}'.format(kwargs['file_path'], '\\')

        try:
            # DataFrame을 xlsx 파일로 변환
            data_frame.to_excel('{}{}'.format(kwargs['file_path'], file_name), index=False)
        except:
            result = False
        else:
            result = True

        return result