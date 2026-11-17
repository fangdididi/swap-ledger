[English](README.md) · **简体中文**

# swap-ledger（换牌台账）

**给视频换品牌，不留旧痕迹。** swap-ledger 是一个智能体技能，用来把参考视频、动效模板或广告翻拍给另一个品牌、产品或客户。它把换牌变成一本可以核对的台账：旧品牌的每一次出现都要有决定，每句新文案都要计时、核对事实，成片最后还要扫描一遍，找出旧品牌留下的任何东西。

## 为什么需要它

换牌视频很少栽在标题上。出问题的往往是：没人重新打过的片尾网址，还写着旧名字的烧录字幕，声音标识，一块几乎就是旧品牌红的背景色，或者品牌换了、宣称却原样留下的“2025 年度第一”角标。swap-ledger 把这些都变成必须关闭的明确条目，全部关闭之后，这条视频才算完成。

## 功能

- **十个识别通道**：文字、标志、产品、界面、配音、字幕、配色、声音、人物、元数据，逐个单独过。
- **四种决定**：每一处出现都定为 SWAP、DROP、NEUTRAL 或 ASK。未决的问题会挡住关卡。
- **权利列**：用于借来的画面、音乐和图库。权利不明或待替换、却仍留在片中的素材会挡住关卡。
- **长度检查**：拿每句新文案的阅读或朗读时间对比它的停留时长（OK / TIGHT / OVER），中英文速度都可以调。
- **宣称检查**：新文案里的数字和最高级说法，必须出自你自己事实表里被引用的条目。
- **残留扫描**：扫字幕、转写稿、抽帧文字、合成源文件和发布元数据。形近拼写（`N0rth-W1nd`）、全角文字、跨行断开的名称，以及与旧配色只差一点 ΔE 的颜色都能抓到。
- **一个结论**：CLEAN / RESIDUE / OPEN。没有成片证据的关卡永远不会给出 CLEAN。
- 只用 Python 标准库，带 12 个测试，哪里都能跑。

## 安装

这个文件夹本身就是技能。把它复制或克隆到你的智能体读取技能的位置：

| 智能体 | 位置 |
|---|---|
| Claude Code | `~/.claude/skills/swap-ledger/`，或项目里的 `.claude/skills/swap-ledger/` |
| Codex | `~/.codex/skills/swap-ledger/`（或在 `AGENTS.md` 里引用 `SKILL.md`） |
| Cursor | `.cursor/skills/swap-ledger/`，或者用项目规则指向 `SKILL.md` |
| 其他智能体 | 文件夹放在任意位置，让智能体去读 `SKILL.md` |

```bash
git clone https://github.com/fangdididi/swap-ledger.git ~/.claude/skills/swap-ledger
```

然后可以这样说：*“用 swap-ledger 把这个模板改成我们品牌的版本。”*

## 用法

```bash
python3 scripts/swapledger.py new rebrand/                      # 生成 swap.json 和 ledger.csv 模板
python3 scripts/swapledger.py fit    rebrand/swap.json rebrand/ledger.csv
python3 scripts/swapledger.py claims rebrand/swap.json rebrand/ledger.csv
python3 scripts/swapledger.py sweep  rebrand/swap.json captions.srt frames.txt comp.css description.txt
python3 scripts/swapledger.py gate   rebrand/swap.json rebrand/ledger.csv captions.srt frames.txt comp.css description.txt
```

退出码 0 表示检查通过，1 表示发现了问题。

## 示例

`examples/oat-remake/` 把一条面包店广告（Brightloaf）翻拍给燕麦棒品牌（Oatfield）：

```
$ python3 scripts/swapledger.py gate examples/oat-remake/swap.json examples/oat-remake/ledger.csv \
    examples/oat-remake/render-captions.srt examples/oat-remake/frame-text.txt \
    examples/oat-remake/composition.css examples/oat-remake/description.txt
RESIDUE examples/oat-remake/composition.css:3: colour #e5592f is within dE 0.7 of old brand #e4572e
RESIDUE examples/oat-remake/description.txt:3: 'Brightloaf' split across lines 2-3
VERDICT RESIDUE
```

“2025 年度第一面包店”角标直接删掉了，没有改写，因为 Oatfield 没有能支撑它的事实。新旁白引用了营养成分标签。授权广告歌被换掉了，因为它的授权不能转给新品牌。最后还是抓到两处残留：一个几乎一模一样的角标颜色，以及一句跨两行断开的、感谢旧品牌的话。

## 文件结构

```
swap-ledger/
├── SKILL.md                 # 技能说明（英文）
├── SKILL.zh-CN.md           # 技能说明（中文）
├── README.md
├── README.zh-CN.md
├── LICENSE
├── scripts/
│   └── swapledger.py        # new / fit / claims / sweep / gate
├── examples/
│   └── oat-remake/          # 换牌卡、台账和成片证据
└── tests/
    └── test_swapledger.py   # python3 -m unittest discover -s tests
```

## 许可证

MIT © fangdididi
