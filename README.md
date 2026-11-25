# Smart Guardian Shield｜智慧防偵測盾牌

> 結合 AI 人員辨識與自動畫面切換的個人防護系統

## 課程資訊

| 項目 | 內容 |
| --- | --- |
| 課號 | BA5077 |
| 課程名稱 | AIoT產品發展實作 |
| 學號 | 113401004 |
| 姓名 | 莊芷寧 |
| 指導老師 | 劉書銘、陳炫碩 |

---

## 1. 作品說明

Smart Guardian Shield 是一套在 Windows 筆電上運作的 AI 防護程式。使用者啟動防護後，系統透過筆電內建鏡頭持續擷取影像，並以 **OpenCV + MobileNet SSD** 辨識畫面中的人員。當有人出現在預先設定的左右兩側監測區域時，程式會自動以全螢幕顯示一個Power BI 風格的數據儀表板畫面，模擬正在處理工作資料的情境，達到即時切換畫面的效果。使用者可按 `Esc` 回到原本畫面，也可隨時暫停或停止防護。

### 核心功能

- **手動啟動／暫停／停止**：由使用者自行決定是否開啟防護
- **AI 人員辨識**：使用 MobileNet SSD 辨識畫面中的 `person`
- **指定區域偵測**：畫面中間為使用者本人所在位置（不觸發），左右兩側為監測區
- **連續畫面確認**：需連續多個畫面偵測到才觸發，降低誤判
- **自動切換畫面**：觸發後全螢幕顯示預先設計的儀表板
- **手動恢復**：按 `Esc` 回到原本畫面，並有冷卻時間避免立刻再次觸發

## 2. AI 相關性

- 使用深度學習物件偵測模型 **MobileNet SSD**（Caffe 格式）進行即時人員辨識
- 透過 OpenCV 的 `dnn` 模組載入模型並對攝影機影像做推論
- 以偵測框的中心位置判斷人員是否進入監測區域，將 AI 辨識結果直接連結到實際行動（切換畫面）

## 3. 與課程內容的關聯

本作品依 Design Thinking 三階段進行：

1. **定義問題**：在公司上班或在開放空間（如：咖啡廳）使用電腦時，旁人常會因為好奇而瞄一眼螢幕。有時是自己剛好在休息，卻怕被誤會在偷懶；有時則是單純不想讓別人看到自己正在做什麼。
2. **創意發想**：後方的人常常無聲無息就走近，使用者很難及時反應。與其手動切換視窗，不如讓系統自動偵測並切換畫面，既能保護隱私，也不會被抓到在「當薪水小偷」。
3. **快速模型與測試**：以 Python + OpenCV 製作原型，先測試鏡頭與人員辨識，再加入左右監測區域與連續畫面確認，最後以 Power BI 風格儀表板作為切換畫面。過程中依測試結果調整參數，逐步改善誤判情況。
   
> 期中提案原本規劃搭配 Raspberry Pi 作為偵測裝置，經老師同意後簡化為直接使用電腦內建鏡頭，其餘 AI 辨識與影像處理的核心內容維持不變。

## 4. 系統架構與使用技術

| 項目 | 使用技術 |
| --- | --- |
| 作業系統 | Windows 11 |
| 攝影設備 | 筆電內建鏡頭 |
| 程式語言 | Python 3.12 |
| AI 辨識 | MobileNet SSD |
| 影像處理 | OpenCV (`opencv-python<5`) |
| 使用者介面 | Tkinter |
| 畫面繪製 | Tkinter Canvas（自行繪製 Power BI 風格儀表板，不需額外套件） |

運作流程：

```
啟動防護 → 擷取鏡頭影像 → MobileNet SSD 辨識人員
        → 判斷是否在左右監測區 → 連續數個畫面成立
        → 全螢幕顯示儀表板頁面 → 使用者按 Esc 恢復
```

## 5. 環境需求

- Windows 10／11
- Python 3.12（其他 3.x 版本應也可執行）
- 具備鏡頭的電腦
- 套件：見 `requirements.txt`

## 6. 安裝與執行方式

**步驟 1：下載本專案**

點選本頁綠色 **Code** → **Download ZIP**，解壓縮後進入資料夾。

**步驟 2：建立虛擬環境並安裝套件**（於命令提示字元 cmd 執行）

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**步驟 3：下載 AI 模型**

本專案不內含模型檔案（約 23 MB）。請從 [chuanqi305/MobileNet-SSD](https://github.com/chuanqi305/MobileNet-SSD) 下載（Code → Download ZIP），並將以下兩個檔案放入專案根目錄下的 `models/` 資料夾：

- `MobileNetSSD_deploy.caffemodel`（位於該專案最外層）
- `MobileNetSSD_deploy.prototxt`（位於該專案的 `voc/` 資料夾內）

完成後結構如下：

完成後結構如下：

```
smart-guardian-shield/
├── models/
│   ├── MobileNetSSD_deploy.caffemodel
│   └── MobileNetSSD_deploy.prototxt
├── source/
│   ├── guardian.py
│   ├── dashboard.py
│   ├── preview_dashboard.py
│   ├── detect_test.py
│   └── camera_test.py
├── evidence/
├── README.md
├── REFLECTION.md
└── requirements.txt
```

**步驟 4：執行**（請在專案根目錄執行）

```
python source/guardian.py
```

## 7. 操作方式

1. 開啟程式後會出現控制視窗，按 **啟動防護**
2. 使用者正常坐在畫面中間時不會觸發
3. 當有人進入畫面左側或右側監測區，程式自動切換為全螢幕的數據儀表板
4. 按鍵盤 **Esc** 回到原本畫面
5. 可隨時按 **暫停／繼續** 或 **停止防護**

可調整參數位於 `source/guardian.py` 開頭：

| 參數 | 說明 | 預設值 |
| --- | --- | --- |
| `CONF_THRESHOLD` | 辨識信心度門檻 | 0.5 |
| `LEFT_ZONE` / `RIGHT_ZONE` | 左右監測區邊界（畫面比例） | 0.25 / 0.75 |
| `HITS_NEEDED` | 連續幾個畫面偵測到才觸發 | 3 |
| `COOLDOWN_SEC` | 關閉假畫面後的冷卻秒數 | 3 |

## 8. 成果證據（EVIDENCE）

所有截圖與影片放在 [`evidence/`](evidence/) 資料夾。

**人員辨識與監測區域**（綠框＝使用者在中間；紅框＝進入監測區）

（請將截圖檔名替換於下方）

<!-- ![辨識畫面](evidence/detect_demo.png) -->

**自動切換畫面**

<!-- ![切換畫面](evidence/decoy_screen.png) -->

**Demo 影片**

（請填入影片檔名或 YouTube 連結）

## 9. 專案結構

```
smart-guardian-shield/
├── README.md                作品說明（本檔）
├── REFLECTION.md            反思與學習心得
├── requirements.txt         Python 套件需求
├── source/                  程式原始碼
│   ├── guardian.py          主程式（Tkinter 介面＋偵測＋畫面切換）
│   ├── dashboard.py         Power BI 風格儀表板繪製
│   ├── preview_dashboard.py 儀表板預覽（不需開鏡頭）
│   ├── detect_test.py       人員辨識與區域判斷測試
│   └── camera_test.py       鏡頭測試
├── evidence/                執行畫面與 Demo
└── models/                  模型放置位置（需自行下載，不含於 Repo）
```

## 10. 隱私與安全說明

- 所有影像僅在本機即時處理，**不儲存、不上傳**
- 本專案不包含任何密碼、API Key 或 Token
