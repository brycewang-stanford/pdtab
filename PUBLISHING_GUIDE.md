# 发布到 PyPI 指南

## 准备工作

1. **安装构建工具**：
```bash
pip install build twine
```

2. **注册 PyPI 账号**：
   - 正式 PyPI: https://pypi.org/account/register/
   - 测试 PyPI: https://test.pypi.org/account/register/

3. **配置 API Token**（推荐）：
   - 在 PyPI 设置中创建 API token
   - 创建 `~/.pypirc` 文件：
```ini
[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-test-api-token-here
```

## 使用 pyproject.toml 的优势

### 为什么使用 pyproject.toml 而不是 setup.py？

1. **现代标准**：
   - PEP 518 标准，Python 官方推荐
   - 声明式配置，更清晰易读
   - 统一的构建系统接口

2. **更好的依赖管理**：
   - 明确分离构建时依赖和运行时依赖
   - 支持可选依赖组（dev, docs等）

3. **工具集成**：
   - 集成 Black、isort、pytest、mypy 等工具配置
   - 一个文件管理所有项目配置

4. **构建系统无关**：
   - 可以轻松切换构建后端（setuptools, flit, poetry等）
   - 更好的隔离性和可重现性

## 发布步骤

### 方法一：使用自动化脚本（推荐）

```bash
# 测试发布
python build_and_publish.py --test

# 正式发布
python build_and_publish.py
```

### 方法二：手动步骤

1. **清理旧文件**：
```bash
rm -rf build/ dist/ *.egg-info/
```

2. **构建包**：
```bash
python -m build
```

3. **检查包**：
```bash
python -m twine check dist/*
```

4. **测试上传**：
```bash
python -m twine upload --repository testpypi dist/*
```

5. **测试安装**：
```bash
pip install --index-url https://test.pypi.org/simple/ pdtab
```

6. **正式上传**：
```bash
python -m twine upload dist/*
```

## 版本管理

当前版本：`0.1.0`

更新版本时，修改 `pyproject.toml` 中的 version 字段：
```toml
[project]
version = "0.1.1"  # 更新这里
```

### 版本号规则（语义化版本）：
- `0.1.0` - 初始版本
- `0.1.1` - 补丁版本（bug修复）
- `0.2.0` - 小版本（新功能）
- `1.0.0` - 大版本（重大更改）

## 检查清单

发布前确认：

- [ ] 所有测试通过
- [ ] 文档更新完整
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] LICENSE 文件存在
- [ ] README.md 内容准确

## 常见问题

### Q: 如何撤回已发布的版本？
A: PyPI 不允许撤回版本，只能发布新版本修复问题。

### Q: 如何更新包的元数据？
A: 修改 pyproject.toml 后重新发布新版本。

### Q: 如何处理依赖冲突？
A: 使用 pip-tools 或 poetry 进行依赖管理。

## 下一步

发布成功后：

1. **创建 GitHub Release**
2. **更新文档网站**
3. **宣传推广**：
   - 在相关论坛发布
   - 写博客介绍
   - 社交媒体分享

## 相关链接

- [PEP 518 - 构建系统要求](https://peps.python.org/pep-0518/)
- [PyPI 上传指南](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [语义化版本](https://semver.org/)
