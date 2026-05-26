# 上传 GitHub 指南

## 1. 创建仓库

在 GitHub 新建仓库：

```text
multibug-agent
```

不要勾选自动生成 README、License 或 .gitignore。

## 2. 本地初始化

```powershell
cd "D:\桌面\自己课题\建议\上传github"
git init
git status
git add .
git commit -m "init multibug agent project"
git branch -M main
git remote add origin https://github.com/你的用户名/multibug-agent.git
git push -u origin main
```

## 3. GitHub About 设置

Description：

```text
Multimodal bug localization and automated test generation platform for Web applications.
```

Topics：

```text
ai-testing
bug-localization
multimodal-ai
llm-agent
deepseek
qwen-vl
streamlit
playwright
pytest
software-testing
test-automation
python
vlm
```

## 4. Release

创建 `v0.1.0` release，标题：

```text
v0.1.0 Initial Demo Release
```
