> 增强兔兔的查询功能，让他可以执行更多操作，相比于原来的兔兔查询，现在他可以

    - 在查询关卡掉落时,显示材料掉率数字
    - 在使用公招查询时，可以不使用百度Api，而是进行本地图片识别查询。（需要安装PaddleOcr）

> 关于PaddleOcr

    - 如果想要使用本地Ocr，请在命令行执行 `pip install paddleocr` 和 `pip install paddlepaddle` 来安装
    - 可执行文件部署方式，暂时无法支持该功能。

> 其他说明

    - 该功能替换了原版的关卡掉落查询功能，您可以选择卸载原版插件（也可以不卸载，并不冲突，本插件优先级更高）
    - 该功能依赖原版的公招查询插件，因此不能卸载原版的公招查询插件。

> [项目地址:Github](https://github.com/hsyhhssyy/amiyabot-arknights-hsyhhssyy-enhanced/)

> [遇到问题可以在这里反馈(Github)](https://github.com/hsyhhssyy/amiyabot-arknights-hsyhhssyy-enhanced/issues/new/)

> [如果上面的连接无法打开可以在这里反馈(Gitee)](https://gitee.com/hsyhhssyy/amiyabot-plugin-bug-report/issues/new)

> [Logo作者:Sesern老师](https://space.bilibili.com/305550122)

|  版本   | 变更  |
|  ----  | ----  |
| 1.0  | 初版登录商店 |
| 1.1  | 适配新版插件商店 |
| 1.2  | 修复了查询已经关闭的关卡会出错的bug |