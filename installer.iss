; ────────────────────────────────────────────────
; TK-OPS Desktop — Inno Setup Script
; 生成安装包: iscc installer.iss
; 需要 Inno Setup 6.x (https://jrsoftware.org/isinfo.php)
; ────────────────────────────────────────────────

#define MyAppName      "TK-OPS 运营助手"
#define MyAppVersion   "1.1.0"
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
UninstallDisplayIcon={app}\TK-OPS.exe
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english";           MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; PyInstaller --onedir 输出的整个 TK-OPS 目录
Source: "dist\TK-OPS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// 卸载时提示是否保留用户数据
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
