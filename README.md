<p align="center">
  <img src="assets/mic_on.png" width="64" height="64" alt="Mic Mute Tray">
</p>

<h1 align="center">Mic Mute Tray</h1>

<p align="center">
  <a href="README.en.md">English</a> | <b>繁體中文</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-brightgreen" alt="Windows">
  <img src="https://img.shields.io/badge/macOS-12%2B-black" alt="macOS">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  輕量系統托盤／選單列工具 — 全域快速鍵一鍵切換麥克風靜音
</p>

---

## 功能特色

- 全域快速鍵切換預設麥克風靜音狀態
- 預設快速鍵：`F13`（適合客製化鍵盤玩家）
- 托盤／選單列圖示隨狀態切換（未靜音／已靜音）
- 自訂各狀態圖示（`.png` / `.ico` / `.bmp`）
- 自訂靜音／取消靜音提示音效（`.wav`）
- 開機自動啟動
- 本機 JSON 設定檔
- 內建預設圖示與音效，遺失時自動產生
- 從系統設定或其他 app 改變靜音狀態時，圖示會自動同步

## 平台支援

| | Windows | macOS |
|---|---|---|
| 麥克風控制 | Core Audio API（`pycaw`） | Core Audio HAL（`ctypes`） |
| 全域快速鍵 | `keyboard` 套件 | Carbon `RegisterEventHotKey` |
| 托盤／選單列 | `pystray` | `NSStatusItem`（AppKit） |
| 音效播放 | `pygame` | `NSSound` |
| 開機啟動 | 登錄檔 `HKCU\...\Run` | launchd LaunchAgent |
| 第三方相依 | 6 個套件 | **無，只用標準函式庫** |

## 推薦給客製化鍵盤玩家

本工具**輕量無負擔**，專為使用**客製化機械鍵盤**（支援 **QMK** / **VIA** 改鍵）的玩家設計。透過 VIA 將鍵盤上不常用的按鍵（例如 `F13`）指定為麥克風切換鍵，再於本工具設定相同的快速鍵，即可擁有一顆專屬的硬體靜音按鈕，不與任何軟體快速鍵衝突。

你還可以：

- **自訂音效** — 換上你喜歡的 WAV 音效（機械鍵盤敲擊聲、提示音、或完全靜音）
- **自訂圖示** — 使用自己的圖片搭配桌面主題或鍵盤風格
- **自訂快速鍵** — 在設定視窗中指定任何按鍵組合

## 系統需求

**共通**

- Python 3.10 或更新版本
- 正常運作的麥克風輸入裝置

**Windows**

- Windows 10 或 Windows 11
- `requirements.txt` 中所列的 Python 套件

**macOS**

- macOS 12 Monterey 或更新版本（選單列圖示使用 SF Symbols）
- **不需要安裝任何第三方套件**
- **不需要「輔助使用」權限** — 全域快速鍵走 Carbon `RegisterEventHotKey`，這是 macOS 上唯一不需授權的系統層快速鍵 API

## 下載

前往 **[Releases](https://github.com/twcat0503/Mic-Mute-Tray/releases/latest)** 下載。每個版本針對 Windows 與 macOS 各提供兩種形式，**兩個平台的檔案完全分開**。

### 免安裝執行檔（不需安裝 Python）

| 平台 | 檔案 |
|---|---|
| Windows 10 / 11 | `MicMuteTray-windows-x64-vX.Y.Z.exe` |
| macOS（Apple Silicon） | `MicMuteTray-macos-arm64-vX.Y.Z.zip` |

> **macOS 首次開啟會被擋下**
>
> 本 app 未經 Apple 開發者簽章與公證，Gatekeeper 會顯示「無法打開，因為無法驗證開發者」。
> 請在 Finder 中**按住 Control 點擊 app → 選擇「開啟」**，或在終端機執行：
>
> ```bash
> xattr -d com.apple.quarantine "Mic Mute Tray.app"
> ```
>
> 若要消除此警告需要 Apple Developer 帳號（每年 99 美元）進行簽章與公證。

### 原始碼壓縮檔（需要 Python 3.10 或更新版本）

| 平台 | 檔案 | 內容 |
|---|---|---|
| Windows | `mic-mute-tray-windows-vX.Y.Z.zip` | 僅含 Windows 後端與 `.bat` 腳本 |
| macOS | `mic-mute-tray-macos-vX.Y.Z.zip` | 僅含 macOS 後端與 `.sh` 腳本 |

Windows 壓縮檔不含任何 `mac_*` 檔案，macOS 壓縮檔也不含任何 `win_*` 檔案。

### 從原始碼取得

```bash
git clone https://github.com/twcat0503/Mic-Mute-Tray.git
cd Mic-Mute-Tray
```

或點擊 GitHub 頁面上的 `Code` → `Download ZIP`（此為完整原始碼，包含兩個平台）。

## 安裝

**Windows**

```bat
install.bat
```

手動安裝：

```powershell
python -m pip install -r requirements.txt
```

**macOS**

```bash
./install.sh
```

macOS 版不需要安裝套件，`install.sh` 只會檢查 Python 版本與 `tkinter` 是否可用。

## 啟動

**Windows**

```bat
launch.bat
```

**macOS**

```bash
./launch.sh
```

工具會在背景啟動，顯示於系統托盤（Windows）或選單列右側（macOS）。macOS 版不會出現在 Dock。

若需除錯，可從終端機直接執行：

```bash
python3 main.py
```

## 使用方式

1. 使用 `launch.bat`（Windows）或 `./launch.sh`（macOS）啟動
2. 按下 `F13`（或你設定的快速鍵）切換麥克風靜音
3. 查看托盤／選單列圖示了解目前狀態
4. 點擊圖示 → 「Settings…」變更選項

macOS 上點擊選單列圖示會展開選單（符合 Apple Human Interface Guidelines 對 menu bar extra 的規範），其中包含目前狀態、`Toggle Mute`、`Settings…` 與 `Quit`。

### 客製化鍵盤設定（VIA / QMK）

1. 開啟 VIA，將 `F13` 指定給鍵盤上一個按鍵
2. 將新按鍵配置寫入鍵盤
3. 在 Mic Mute Tray 設定中設定相同快速鍵
4. 按下該實體按鍵即可切換靜音 — 無軟體衝突

## 設定

- **快速鍵** — Windows 版按下任意按鍵組合即可錄製；macOS 版從下拉選單挑選按鍵並勾選 `⌃` `⌥` `⇧` `⌘`
- **自訂圖示** — 選擇 `.png` / `.ico` / `.bmp` 檔案
- **自訂提示音效** — 選擇 `.wav` 檔案
- **開機自動啟動** — 隨系統登入自動啟動

設定檔位置：

- Windows：程式資料夾內的 `config.json`
- macOS：`~/Library/Application Support/Mic Mute Tray/config.json`

可參考 `config.example.json` 的預設值：

```json
{
  "hotkey": "F13",
  "mic_on_icon": null,
  "mic_off_icon": null,
  "mic_on_sound": null,
  "mic_off_sound": null,
  "autostart": false
}
```

## macOS 設計說明

macOS 版依照 Apple 的 Human Interface Guidelines 設計：

- **Template image** — 預設圖示使用 SF Symbols 的 `mic.fill` 與 `mic.slash.fill`，由系統自動配色，在淺色／深色選單列與被選取時都能正確顯示
- **顯示 menu 而非 popover** — 點擊圖示展開標準 `NSMenu`
- **選單列 agent** — 執行時設為 `NSApplicationActivationPolicyAccessory`，不佔用 Dock，也不建立應用程式選單
- **設定檔位置** — 放在 `~/Library/Application Support/`，符合 Apple 對 per-user app data 的慣例
- **登入啟動** — 使用 `~/Library/LaunchAgents` 的 launchd agent。啟用後會出現在「系統設定 → 一般 → 登入項目 → 允許在背景執行」

由於 AppKit 與 Tkinter 都必須佔用主執行緒，macOS 版讓 AppKit 掌管主迴圈，設定視窗則以獨立子程序開啟。常駐的選單列 agent 因此完全不會載入 Tkinter。

## 從原始碼建置執行檔

`scripts/` 內含打包用的腳本與 PyInstaller spec。

**分平台原始碼壓縮檔**（任何平台皆可執行）：

```bash
python3 scripts/package.py --clean
# 產出 dist/mic-mute-tray-windows-vX.Y.Z.zip
#      dist/mic-mute-tray-macos-vX.Y.Z.zip
```

腳本會檢查兩個壓縮檔沒有混入對方平台的檔案，混到就直接失敗。

**macOS `.app`**（需在 macOS 上執行）：

```bash
uvx --python "$(which python3)" --from pyinstaller pyinstaller \
  --noconfirm --distpath dist --workpath build/pyi scripts/macos.spec
```

**Windows `.exe`**（需在 Windows 上執行）：先用 `install.bat` 裝好相依套件與 `pyinstaller`，再執行：

```bat
pyinstaller --noconfirm --distpath dist --workpath build/pyi scripts/windows.spec
```

PyInstaller 無法跨平台編譯，因此 `.github/workflows/release.yml` 會在推送 `v*` tag 時，由 GitHub Actions 的 windows 與 macOS runner 各自建置，再彙整成一個 draft release。

## 專案結構

```text
main.py               應用程式進入點與平台分派
config_manager.py     設定檔載入與儲存
asset_generator.py    預設圖示與音效產生器、素材路徑解析
settings_window.py    設定視窗（Tkinter）

mic_control.py        麥克風控制 — 平台分派
hotkey_manager.py     全域快速鍵 — 平台分派
sound_manager.py      提示音效 — 平台分派
startup_manager.py    開機啟動 — 平台分派

win_tray_app.py       Windows 系統托盤（pystray）
win_mic_control.py    Windows 麥克風控制（pycaw）
win_hotkey.py         Windows 全域快速鍵（keyboard）
win_sound.py          Windows 音效播放（pygame）
win_startup.py        Windows 開機啟動（登錄檔）

mac_app.py            macOS 選單列 agent（NSStatusItem）
mac_objc.py           Objective-C runtime／AppKit 的 ctypes bridge
mac_mic_control.py    macOS 麥克風控制（Core Audio HAL）
mac_hotkey.py         macOS 全域快速鍵（Carbon RegisterEventHotKey）
mac_keycodes.py       快速鍵字串與 macOS virtual key code 轉換
mac_sound.py          macOS 音效播放（NSSound）
mac_startup.py        macOS 登入啟動（launchd LaunchAgent）

assets/               內建預設圖示與音效
scripts/              打包腳本與 PyInstaller spec
.github/workflows/    Release CI（分平台建置）
```

## 疑難排解

### 快速鍵無效

- 在設定中更換其他快速鍵
- 避免使用已被其他應用程式佔用的按鍵
- macOS：若該組合已被系統或其他 app 註冊，`RegisterEventHotKey` 會失敗，終端機會顯示警告訊息
- 執行 `python3 main.py` 查看錯誤訊息

### 圖示消失

- Windows：展開工作列的隱藏圖示區域
- macOS：選單列空間不足時系統會隱藏部分項目，可先關閉其他選單列 app
- 重新啟動工具

### 麥克風狀態無法切換

- 確認系統已設定預設輸入裝置
- Windows：檢查隱私權設定中的麥克風存取權限
- macOS：部分外接音訊介面不提供 mute 屬性，此時本工具會改為將輸入音量降到 0，取消靜音時還原原本音量
- 確認輸入裝置未被停用

### 開機自動啟動無效

- 在設定中先關閉再重新開啟該選項
- 確認啟用後未移動工具資料夾
- macOS：到「系統設定 → 一般 → 登入項目」確認 Mic Mute Tray 已被允許在背景執行
- 執行 `python3 main.py` 查看錯誤

## 授權條款

MIT License。詳見 [LICENSE](LICENSE)。
