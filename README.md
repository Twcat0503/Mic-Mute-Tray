<p align="center">
  <img src="assets/mic_on.png" width="64" height="64" alt="Mic Mute Tray">
</p>

<h1 align="center">Mic Mute Tray</h1>

<p align="center">
  <a href="README.en.md">English</a> | <b>繁體中文</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-brightgreen" alt="Windows">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  輕量 Windows 系統托盤工具 — 全域快速鍵一鍵切換麥克風靜音
</p>

---

## 功能特色

- 全域快速鍵切換預設麥克風靜音狀態
- 預設快速鍵：`F13`（適合客製化鍵盤玩家）
- 托盤圖示隨狀態切換（未靜音／已靜音）
- 自訂各狀態托盤圖示（`.png` / `.ico` / `.bmp`）
- 自訂靜音／取消靜音提示音效（`.wav`）
- 開機自動啟動
- 本機 JSON 設定檔
- 內建預設圖示與音效，遺失時自動產生

## 推薦給客製化鍵盤玩家

本工具**輕量無負擔**，專為使用**客製化機械鍵盤**（支援 **QMK** / **VIA** 改鍵）的玩家設計。透過 VIA 將鍵盤上不常用的按鍵（例如 `F13`）指定為麥克風切換鍵，再於本工具設定相同的快速鍵，即可擁有一顆專屬的硬體靜音按鈕，不與任何軟體快速鍵衝突。

你還可以：

- **自訂音效** — 換上你喜歡的 WAV 音效（機械鍵盤敲擊聲、提示音、或完全靜音）
- **自訂托盤圖示** — 使用自己的圖片搭配桌面主題或鍵盤風格
- **自訂快速鍵** — 在設定視窗中錄製任何按鍵組合

## 系統需求

- Windows 10 或 Windows 11
- Python 3.10 或更新版本
- 正常運作的麥克風輸入裝置
- `requirements.txt` 中所列的 Python 套件

本工具透過 Windows 音訊 API（`pycaw` + `comtypes`）運作，不支援 macOS 或 Linux。

## 下載

```powershell
git clone https://github.com/<your-user>/mic-mute-tray.git
cd mic-mute-tray
```

或點擊 GitHub 頁面上的 `Code` → `Download ZIP`，解壓縮後開啟資料夾。

## 安裝

```bat
install.bat
```

手動安裝：

```powershell
python -m pip install -r requirements.txt
```

建議開發時使用虛擬環境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 啟動

```bat
launch.bat
```

工具會在背景啟動，顯示於 Windows 系統托盤。若需除錯，可從終端機執行：

```powershell
python main.py
```

## 使用方式

1. 使用 `launch.bat` 啟動
2. 按下 `F13`（或你設定的快速鍵）切換麥克風靜音
3. 查看系統托盤圖示了解目前狀態
4. 在托盤圖示上按右鍵 → 「Settings」變更選項

### 客製化鍵盤設定（VIA / QMK）

1. 開啟 VIA，將 `F13` 指定給鍵盤上一個按鍵
2. 將新按鍵配置寫入鍵盤
3. 在 Mic Mute Tray 設定中設定相同快速鍵
4. 按下該實體按鍵即可切換靜音 — 無軟體衝突

## 設定

- **快速鍵錄製** — 按下任意按鍵組合即可擷取
- **自訂托盤圖示** — 選擇 `.png` / `.ico` / `.bmp` 檔案
- **自訂提示音效** — 選擇 `.wav` 檔案
- **開機自動啟動** — 隨 Windows 登入自動啟動

設定儲存於 `config.json`，可參考 `config.example.json` 的預設值：

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

## 專案結構

```text
main.py               應用程式進入點
tray_app.py           系統托盤、選單、快速鍵流程與狀態更新
settings_window.py    設定視窗（Tkinter）
mic_control.py        Windows 麥克風靜音控制
config_manager.py     設定檔載入與儲存
hotkey_manager.py     全域快速鍵註冊
sound_manager.py      提示音效播放
startup_manager.py    開機啟動登錄輔助
asset_generator.py    預設圖示與音效產生器
assets/               內建預設圖示與音效
```

## 疑難排解

### 快速鍵無效

- 在設定中更換其他快速鍵
- 避免使用已被其他應用程式佔用的按鍵
- 執行 `python main.py` 查看錯誤訊息

### 托盤圖示消失

- 展開 Windows 工作列的隱藏圖示區域
- 重新啟動工具
- 重新安裝套件：`python -m pip install -r requirements.txt`

### 麥克風狀態無法切換

- 確認 Windows 已設定預設輸入裝置
- 檢查 Windows 隱私權設定中的麥克風存取權限
- 確認輸入裝置未被停用

### 開機自動啟動無效

- 在設定中先關閉再重新開啟「Start with Windows」
- 確認啟動後未移動工具資料夾
- 執行 `python main.py` 查看錯誤

## 授權條款

MIT License。詳見 [LICENSE](LICENSE)。
