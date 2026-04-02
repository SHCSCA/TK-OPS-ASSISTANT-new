; ------------------------------------------------
; TK-OPS Desktop Alpha - Inno Setup Script
; 生成安装包: iscc installer.iss
; 依赖: 先执行 scripts\release.ps1，生成 dist-alpha\TK-OPS-Alpha
; ------------------------------------------------

#define MyAppName      "TK-OPS 运营助手"
#define MyAppVersion   "1.3.0"
#define MyAppPublisher "TK-OPS"
#define MyAppExeName   "TK-OPS.exe"
#define MyAppURL       "https://github.com/your-org/tk-ops"

[Setup]
AppId={{B5E3F1A0-2D4C-4E6F-9A1B-8C7D3E5F0A2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\TK-OPS
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=TK-OPS-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=tkops.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 新单壳 alpha 产物目录，由 scripts\release.ps1 生成
Source: "dist-alpha\TK-OPS-Alpha\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\TK-OPS-ASSISTANT');
    if DirExists(DataDir) then
    begin
      if MsgBox('是否删除用户数据（数据库、日志、设置）？' + #13#10 + DataDir,
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;
