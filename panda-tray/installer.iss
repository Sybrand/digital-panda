; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Digital Panda - Cloud Storage Synchronisation Client"
#define MyAppVersion "0.13"
#define MyAppPublisher "Digital Panda"
#define MyAppURL "http://www.digitalpanda.co.za"
#define MyAppExeName "panda-tray-w.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{022B66AF-4266-4535-9FBE-3686871222D8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\Digital Panda
DefaultGroupName=Digital Panda
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE.rtf
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes
SignTool=Standard

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\panda-tray-w.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\python27.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Digital Panda Tray Application-{#MyAppVersion}.win32\*"; DestDir: "{app}\Digital Panda Tray Application-{#MyAppVersion}.win32"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

