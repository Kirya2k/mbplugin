@echo OFF
%~d0 

cd "%~dp0"
echo ���ᮡ�ࠥ� DLL 
call dllsource\compile_all_p.bat

cd "%~dp0"
echo �஢��塞 �� �� ࠡ�⠥�
call plugin\test_mbplugin_dll_call.bat p_test1 123 456 
