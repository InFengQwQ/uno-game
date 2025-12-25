# 贡献指南 / Contributing Guide

[中文](#中文) | [English](#english)

---

## 中文

### 何时提交 Pull Request

在提交 Pull Request (PR) 之前，请确保：

#### ✅ 准备就绪的标准

1. **代码已完成**
   - 所有功能已实现并且能正常工作
   - 代码没有明显的错误或 bug
   - 不要提交标记为"待debug"、"待修复"、"待完成"的代码

2. **代码质量**
   - 代码符合项目的编码风格
   - 变量和函数命名清晰易懂
   - 复杂逻辑有适当的注释
   - 移除了调试代码和注释掉的代码

3. **测试**
   - 在本地测试过所有更改
   - 确保没有破坏现有功能
   - 新功能有基本的测试验证

4. **提交信息**
   - 使用清晰的提交信息描述更改内容
   - 避免使用模糊的描述如"修复bug"、"更新代码"
   - 提交信息应该说明"做了什么"而不是"要做什么"

#### ❌ 不合理的 Pull Request

以下情况下的 PR 被认为是**不合理的**：

- ❌ 提交包含明确标注"待debug"、"待修复"的代码
- ❌ 提交未经测试的大规模重构
- ❌ 提交明知有错误但打算"稍后修复"的代码
- ❌ 提交不完整的功能（除非明确说明这是 WIP/草稿 PR）

#### 📝 合理使用草稿 PR

如果你的代码还在开发中，需要反馈或讨论，可以：

1. 创建**草稿 PR (Draft Pull Request)**
2. 在标题中明确标注 `[WIP]` 或 `[Draft]`
3. 在描述中说明：
   - 当前的开发状态
   - 还需要完成的工作
   - 需要的帮助或反馈

### 提交信息规范

#### 好的提交信息示例：

```
feat: 实现多人游戏房间功能

- 添加房间创建和加入逻辑
- 实现玩家列表的同步
- 支持密码保护的房间
```

```
fix: 修复抽牌时的卡牌重复问题

修复了在牌堆为空时重新洗牌导致的卡牌重复bug
```

```
refactor: 统一消息收发接口

将TCP消息收发逻辑封装到独立的工具函数中，便于后续维护和扩展
```

#### 不好的提交信息示例：

```
feat: （待debug与一致化）重构消息收发逻辑...
```
> ❌ 包含"待debug"说明代码未完成

```
更新代码
```
> ❌ 过于模糊，没有说明具体做了什么

```
修复bug
```
> ❌ 没有说明修复了什么bug

### Pull Request 模板

提交 PR 时，建议包含以下信息：

```markdown
## 更改说明
简要描述本次更改的内容和目的

## 更改类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 代码重构 (refactor)
- [ ] 文档更新 (docs)
- [ ] 性能优化 (perf)
- [ ] 测试相关 (test)

## 测试
描述如何测试这些更改：
- [ ] 本地测试通过
- [ ] 没有破坏现有功能

## 相关 Issue
如适用，请引用相关的 issue 编号

## 备注
其他需要说明的信息
```

---

## English

### When to Submit a Pull Request

Before submitting a Pull Request (PR), ensure that:

#### ✅ Ready for Review Criteria

1. **Code is Complete**
   - All features are implemented and working properly
   - Code has no obvious errors or bugs
   - Do not submit code marked as "to be debugged", "to be fixed", or "to be completed"

2. **Code Quality**
   - Code follows the project's coding style
   - Variables and functions have clear, meaningful names
   - Complex logic has appropriate comments
   - Debug code and commented-out code are removed

3. **Testing**
   - All changes have been tested locally
   - Existing functionality is not broken
   - New features have basic test coverage

4. **Commit Messages**
   - Use clear commit messages describing the changes
   - Avoid vague descriptions like "fix bug", "update code"
   - Commit messages should describe "what was done" not "what needs to be done"

#### ❌ Unreasonable Pull Requests

PRs are considered **unreasonable** in the following cases:

- ❌ Submitting code explicitly marked as "to be debugged" or "to be fixed"
- ❌ Submitting large-scale refactoring without testing
- ❌ Submitting code with known errors, planning to "fix later"
- ❌ Submitting incomplete features (unless clearly marked as WIP/Draft PR)

#### 📝 Proper Use of Draft PRs

If your code is still in development and you need feedback or discussion:

1. Create a **Draft Pull Request**
2. Clearly mark the title with `[WIP]` or `[Draft]`
3. In the description, explain:
   - Current development status
   - Work that still needs to be completed
   - Help or feedback needed

### Commit Message Guidelines

#### Good Commit Message Examples:

```
feat: implement multiplayer room functionality

- Add room creation and join logic
- Implement player list synchronization
- Support password-protected rooms
```

```
fix: resolve card duplication issue when drawing

Fixed a bug where reshuffling when the deck is empty caused card duplication
```

```
refactor: unify message send/receive interface

Encapsulate TCP message send/receive logic into separate utility functions
for easier maintenance and extension
```

#### Bad Commit Message Examples:

```
feat: (to be debugged and unified) refactor message logic...
```
> ❌ Contains "to be debugged" indicating incomplete code

```
update code
```
> ❌ Too vague, doesn't explain what was done

```
fix bug
```
> ❌ Doesn't specify which bug was fixed

### Pull Request Template

When submitting a PR, consider including:

```markdown
## Description
Brief description of the changes and their purpose

## Type of Change
- [ ] New feature (feat)
- [ ] Bug fix (fix)
- [ ] Code refactoring (refactor)
- [ ] Documentation update (docs)
- [ ] Performance improvement (perf)
- [ ] Testing (test)

## Testing
Describe how these changes were tested:
- [ ] Local testing passed
- [ ] No existing functionality broken

## Related Issues
If applicable, reference related issue numbers

## Notes
Any other relevant information
```

---

## 关于当前提交的说明 / About the Current Submission

如果你提交的代码包含"待debug"、"待修复"等标记，这通常被认为是不合理的，因为：

1. **代码质量标准**：提交的代码应该是经过测试、可以正常工作的代码
2. **代码审查效率**：审查者需要审查完成的代码，而不是还在开发中的代码
3. **项目稳定性**：合并未完成的代码可能会影响项目的稳定性

**建议做法**：
- 如果代码还未完成，请继续在本地开发，直到完成并测试通过后再提交 PR
- 如果需要早期反馈，请创建**草稿 PR (Draft PR)**并明确标注状态
- 如果只是小的改进空间，可以在 PR 描述中说明，但核心功能应该是完整的

If your submitted code contains markers like "to be debugged" or "to be fixed", this is generally considered unreasonable because:

1. **Code Quality Standards**: Submitted code should be tested and working properly
2. **Review Efficiency**: Reviewers need to review completed code, not code still in development
3. **Project Stability**: Merging incomplete code can affect project stability

**Recommended Approach**:
- If code is not yet complete, continue local development until it's finished and tested before submitting a PR
- If you need early feedback, create a **Draft PR** and clearly mark the status
- If there's only minor room for improvement, you can note it in the PR description, but core functionality should be complete
