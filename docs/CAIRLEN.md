# Cairlen 自部署版本

- GitHub 源码： https://github.com/eaiu/wloc
- Pages 选点网页： https://wloc-cairlen.pages.dev/
- Loon 插件： https://raw.githubusercontent.com/eaiu/wloc/refs/heads/main/modules/wloc.lpx
- 快捷指令解析： https://wloc-cairlen.pages.dev/api/parse

模块及网页的源码链接由 `project.config.json` 统一配置，运行 `npm run configure` 生成。
修改配置不会自动更新手机上已安装的快捷指令，需要重新导入签名后的文件。

## 生成快捷指令

`shortcuts/templates/set-location.plist` 是从维护版公开 iCloud 分享导出的未签名模板。
它保留上游动作和变量；生成脚本替换解析服务、订阅地址，并校验 Apple 变量引用偏移。

```sh
python3 scripts/configure-shortcut.py
shortcuts sign --mode anyone \
  --input build/shortcuts/WLOC-set-location-Cairlen.unsigned.shortcut \
  --output worker/dist/shortcuts/WLOC-set-location-Cairlen.shortcut
shortcuts sign --mode anyone \
  --input build/shortcuts/WLOC-restore-location-Cairlen.unsigned.shortcut \
  --output worker/dist/shortcuts/WLOC-restore-location-Cairlen.shortcut
```

部署后可从下列地址下载个人版快捷指令：

https://wloc-cairlen.pages.dev/shortcuts/WLOC-set-location-Cairlen.shortcut

https://wloc-cairlen.pages.dev/shortcuts/WLOC-restore-location-Cairlen.shortcut

保留 `https://gs-loc.apple.com/wloc-settings/save`：它是 Loon 在手机上拦截的储存路径。
恢复快捷指令只需请求该地址并附加 `?action=clear`，无需 Pages 解析服务。

## Cloudflare Pages 配置

连接 `eaiu/wloc`，生产分支为 `main`：

- 根目录：`worker`
- 构建命令：`npm ci`
- 构建输出目录：`dist`
- 环境变量：`NODE_VERSION=24`
- 项目名：`wloc-cairlen`

Pages 会同时编译 `worker/functions`。这不能部署为纯静态 GitHub Pages。
命令行部署方式：在 `worker` 目录运行 `npx wrangler pages deploy --branch main`。

本定制不改变上游的 iOS 兼容性；部署成功不代表定位拦截在当前系统上一定有效。
