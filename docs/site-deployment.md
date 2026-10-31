# Project homepage publishing / 项目主页发布

## 中文

静态主页源码位于 `docs/index.html`，图形与图标位于 `docs/site-assets/`。页面不依赖外部前端框架或 CDN。

发布前需要仓库管理员在 GitHub 仓库设置中启用 GitHub Pages：

1. 打开 **Settings → Pages**。
2. 在 **Build and deployment** 中选择 **Deploy from a branch**。
3. 选择 `main` 分支和 `/docs` 目录并保存。
4. 首次部署后核对公开 URL、移动端布局、导航、语言切换和图片加载。
5. 将仓库主页 URL 设置为实际生成的 Pages 地址。

本次只提交网站源码和静态资源，不启用 Pages、不触发外部部署，也不宣称主页已经上线。

## English

The static homepage source is `docs/index.html`; visuals and icons live in `docs/site-assets/`. The page has no external frontend framework or CDN dependency.

A repository administrator must enable GitHub Pages before the site is public:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select branch `main` and folder `/docs`, then save.
4. After the first deployment, verify the public URL, responsive layout, navigation, language switch and asset loading.
5. Set the repository homepage URL to the actual Pages address.

This change prepares the website source only. It does not enable Pages, trigger an external deployment or claim that the homepage is live.
