import time
import yaml
from tqdm import tqdm
from library import sap_down
from library import sap_utils

if __name__ == '__main__':
    # Read the "sap_setting.yaml" file for setting
    with open('.\\sap_setting.yaml', 'r', encoding='utf-8') as f:
        sap_setting = yaml.load(f, Loader=yaml.FullLoader)

    # sap_setting에 run_sap_script의 리스트를 읽어 해당 리스트에 있는 Script를 순서대로 실행
    for i, operation in enumerate(sap_setting['run_sap_script'], start=1):
        # 실행 할 SAP Script(operation)의 Setting 파일을 읽어 script_setting에 저장
        with open('{}{}.yaml'.format(sap_setting['sap_script_path'], operation), 'r', encoding='utf-8') as f:
            script_setting = yaml.load(f, Loader=yaml.FullLoader)
        
        # 실행 할 SAP Script(operation)의 이름으로 객체 생성
        if i == 1:
            locals()[operation] = sap_down.SapDown(operation, script_setting, sap_setting=sap_setting)
        else:
            locals()[operation] = sap_down.SapDown(operation, script_setting)
        print("====== {}/{} Start -{}- Script ===========".format(str(i), len(sap_setting['run_sap_script']), operation))

        # 생성된 객체의 Reference DataFrame이 필요하면 다른 객체의 My Dataframe을 복사 해줌
        if len(script_setting['reference_data']) != 0:
            locals()[operation].set_reference_df(locals()[script_setting['reference_data']].get_my_df())
        
        # 다운 받은 파일 저장 할 폴더 생성
        sap_utils.SapUtils.make_file_path(script_setting['file_save_path'])
        
        # 임시 폴더 및 다운 받은 파일 저장 폴더의 기존 파일 삭제
        sap_utils.SapUtils.delete_file(file_path=sap_setting['tempfile_save_path'], file_all=True)
        sap_utils.SapUtils.delete_file(file_path=script_setting['file_save_path'], file_all=True)
        
        # SAP Client 재시작
        locals()[operation].restart_sap_client()
        
        # SAP Script 실행하여 파일 다운로드
        file_name_list = locals()[operation].down_file_sap()
    
    locals()[sap_setting['run_sap_script'][0]].end_sap_client()
    print("실행이 완료 되었습니다.")
    time.sleep(600)