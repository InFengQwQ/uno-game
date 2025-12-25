# UNO 游戏 / UNO Game

一个基于 Python 和 Pygame 的多人 UNO 卡牌游戏。

A multiplayer UNO card game based on Python and Pygame.

## 功能特性 / Features

- 🎮 单人和多人游戏模式 / Single and multiplayer game modes
- 🌐 网络对战支持 / Network battle support
- 🎨 图形化界面 / Graphical user interface
- 🃏 完整的 UNO 规则实现 / Complete UNO rules implementation

## 环境要求 / Requirements

- Python >= 3.11
- pygame >= 2.0.0

## 安装 / Installation

```bash
# 克隆仓库 / Clone the repository
git clone https://github.com/InFengQwQ/uno-game.git
cd uno-game

# 安装依赖 / Install dependencies
pip install -r requirements.txt
```

## 运行 / Running

```bash
python main.py
```

## 项目结构 / Project Structure

```
uno-game/
├── assets/          # 游戏资源（图片、字体、音效）/ Game assets (images, fonts, sounds)
├── config/          # 配置文件 / Configuration files
├── docs/            # 文档 / Documentation
├── multi/           # 多人游戏网络模块 / Multiplayer networking module
├── ui/              # 用户界面组件 / UI components
├── uno/             # 游戏核心逻辑 / Game core logic
├── main.py          # 主程序入口 / Main entry point
└── requirements.txt # Python 依赖 / Python dependencies
```

## 游戏规则 / Game Rules

详细的游戏规则请参考 [docs/rules.md](docs/rules.md)。

For detailed game rules, please refer to [docs/rules.md](docs/rules.md).

## 贡献指南 / Contributing

我们欢迎所有形式的贡献！在提交 Pull Request 之前，请务必阅读我们的[贡献指南](CONTRIBUTING.md)。

We welcome all forms of contributions! Before submitting a Pull Request, please read our [Contributing Guide](CONTRIBUTING.md).

### 重要提示 / Important Notes

- ✅ 请确保代码已经完成并经过测试后再提交 PR / Please ensure code is complete and tested before submitting a PR
- ✅ 不要提交包含"待debug"、"待修复"标记的代码 / Do not submit code with "to be debugged" or "to be fixed" markers
- ✅ 使用清晰的提交信息 / Use clear commit messages
- ✅ 如需早期反馈，请使用草稿 PR / Use draft PRs for early feedback

详细信息请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 构建 / Building

项目提供了两种构建方式：

The project provides two build options:

```bash
# 使用 PyInstaller / Using PyInstaller
pyinstaller_build.bat

# 使用 Nuitka / Using Nuitka
nuitka_build.bat
```

## 许可证 / License

本项目目前没有明确的许可证。如果您想使用或贡献代码，请先联系项目维护者。

This project currently has no explicit license. If you want to use or contribute code, please contact the project maintainer first.

## 联系方式 / Contact

- 作者 / Author: InFeng
- Email: 2961282519@qq.com

## 致谢 / Acknowledgments

感谢所有为这个项目做出贡献的开发者。

Thanks to all developers who have contributed to this project.

---

**注意 / Note**: 本项目仍在积极开发中。如有问题或建议，欢迎提出 Issue。

**Note**: This project is still under active development. Feel free to open an issue if you have any questions or suggestions.
