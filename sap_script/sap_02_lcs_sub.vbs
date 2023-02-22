' Arg(0) : tcode - "/nYMIIPICK"
' Arg(1) : plant code - "1000"
' Arg(2) : 시작 일자 - "2022.11.01"
' Arg(3) : 종료 일자 - "2022.12.30"
' Arg(4) : 파일 저장 위치 - "C:\Users\ec20685\Downloads\"
' Arg(5) : 파일 이름 - "12345.txt"
' Arg(6) : 파일 인코딩 - "0000"
' Arg(7) : 라인 코드 - "LCS-E10"
Dim Arg
Set Arg = WScript.Arguments
On Error Resume Next

If Not IsObject(application) Then
   Set SapGuiAuto  = GetObject("SAPGUI")
   Set application = SapGuiAuto.GetScriptingEngine
End If
If Not IsObject(connection) Then
   Set connection = application.Children(0)
End If
If Not IsObject(session) Then
   Set session    = connection.Children(0)
End If
If IsObject(WScript) Then
   WScript.ConnectObject session,     "on"
   WScript.ConnectObject application, "on"
End If
session.findById("wnd[0]").maximize
session.findById("wnd[0]/tbar[0]/okcd").text = Arg(0)
session.findById("wnd[0]").sendVKey 0
session.findById("wnd[0]/usr/ctxtP_WERKS").text = Arg(1)
session.findById("wnd[0]/usr/ctxtS_GSTRP-LOW").text = Arg(2)
session.findById("wnd[0]/usr/ctxtS_GSTRP-HIGH").text = Arg(3)
session.findById("wnd[0]/usr/ctxtS_PICKA-LOW").text = Arg(7)
session.findById("wnd[0]/usr/ctxtS_PICKA-LOW").setFocus
session.findById("wnd[0]/usr/ctxtS_PICKA-LOW").caretPosition = 7
session.findById("wnd[0]/tbar[1]/btn[8]").press
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus
session.findById("wnd[1]/tbar[0]/btn[0]").press
session.findById("wnd[1]/usr/ctxtDY_PATH").text = Arg(4)
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = Arg(5)
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = Arg(6)
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").setFocus
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
session.findById("wnd[1]/tbar[0]/btn[0]").press