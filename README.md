# sap_down_by_script

## SAP down by vbs Script 프로그램
SAP Client에서 제공하는 Visual Basic Script 녹화 재생 기능을 이용한 SAP Data Download 프로그램입니다.(Python으로 제작)
해당 프로그램은 SAP에서 반복적으로 대량의 데이터를 받기 위해 만들었습니다.

## 프로그램 사용에 필요한 사항
#### SAP Client
1. SAP client
1. SAP의 "Script Recording and Playback" 권한 (없을 경우 SAP 담당자에게 문의)
#### Python package(컴파일된 프로그램 실행시 필요 없음)
1. Pandas
1. PyYaml
<code>/ pip install pandas pyyaml</code>
## 프로그램 구조
```bash
├── library
│   ├── sap_down.py
│   └── sap_utils.py
├── sap_script
│   ├── template.vbs
│   └── template.yaml
├── sap_down_by_script.py
└── sap_setting.yaml
``` 
1. sap_down_by_script.py : 프로그램 실행 파일
1. sap_setting.yaml : 프로그램 Global setting 파일
1. library/sap_down.py : SAP Data 다운받는 Class 파일
1. library/sap_utils.py : 프로그램 작동에 필요한 Util Class
1. sap_script/template.vbs : SAP client 자동 실행용 Visual Basic Script
1. sap_script/template.yaml : Visual Basic Script 작동에 필요한 설정 파일

## 프로그램 작동 로직
